# src/ml/movie_recommender.py
import sys
import json
import os
import pandas as pd
from pymongo import MongoClient
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MultiLabelBinarizer
from scipy.sparse import hstack
from bson.objectid import ObjectId
from scipy.sparse import csr_matrix

def get_recommendations(movie_id_to_recommend=None, num_recommendations=10, search_keywords=None, user_preferences=None):
    """
    Hàm này kết nối tới MongoDB, lấy dữ liệu phim,
    tính toán độ tương đồng và trả về gợi ý.
    Có thể gợi ý theo movie_id, search_keywords, hoặc user_preferences.
    """
    MONGODB_URI = os.getenv("MONGODB_URI")
    if not MONGODB_URI:
        return {"error": "Biến môi trường MONGODB_URI không được thiết lập."}
    
    DB_NAME = MONGODB_URI.split('/')[-1].split('?')[0]

    client = None
    try:
        client = MongoClient(MONGODB_URI)
        db = client[DB_NAME]
        movies_collection = db['embedded_movies']
        
        movies_data = list(movies_collection.find({}, {
            '_id': 1, 'title': 1, 'genres': 1, 'plot': 1, 'fullplot': 1,
            'cast': 1, 'directors': 1, 'writers': 1, 'awards': 1, 'poster': 1,
            'languages': 1, 'released': 1, 'lastupdated': 1, 'year': 1, 'imdb': 1,
            'countries': 1, 'type': 1, 'runtime': 1
        }))
        
        if not movies_data:
            return {"error": "Không tìm thấy dữ liệu phim trong collection 'embedded_movies'."}

        df = pd.DataFrame(movies_data)
        df.rename(columns={'_id': 'id'}, inplace=True)
        
        # --- SỬA LỖI: DI CHUYỂN DÒNG ĐỊNH NGHĨA 'indices' LÊN ĐÂY ---
        indices = pd.Series(df.index, index=df['id']).drop_duplicates()
        # --- HẾT SỬA LỖI ---
        
        # Xử lý dữ liệu thiếu: thay thế NaN bằng chuỗi rỗng cho các cột text, danh sách rỗng cho các cột list
        df['plot'] = df['plot'].fillna('')
        df['fullplot'] = df['fullplot'].fillna('')
        
        for col in ['genres', 'cast', 'directors', 'writers', 'languages', 'countries']:
            df[col] = df[col].apply(lambda x: x if isinstance(x, list) else [])

        # Mã hóa One-Hot cho các trường dạng mảng
        mlb_genres = MultiLabelBinarizer()
        genres_matrix = mlb_genres.fit_transform(df['genres'])
        
        mlb_cast = MultiLabelBinarizer()
        cast_matrix = mlb_cast.fit_transform(df['cast'])

        mlb_directors = MultiLabelBinarizer()
        directors_matrix = mlb_directors.fit_transform(df['directors'])

        mlb_writers = MultiLabelBinarizer()
        writers_matrix = mlb_writers.fit_transform(df['writers'])

        mlb_languages = MultiLabelBinarizer()
        languages_matrix = mlb_languages.fit_transform(df['languages'])

        mlb_countries = MultiLabelBinarizer()
        countries_matrix = mlb_countries.fit_transform(df['countries'])

        # Vector hóa TF-IDF cho các trường văn bản
        tfidf_plot = TfidfVectorizer(stop_words='english', max_features=5000)
        plot_tfidf_matrix = tfidf_plot.fit_transform(df['plot'] + ' ' + df['fullplot'])
        
        # Ghép nối tất cả các ma trận thành một ma trận đặc trưng lớn
        feature_matrix = hstack([
            genres_matrix,
            cast_matrix,
            directors_matrix,
            writers_matrix,
            languages_matrix,
            countries_matrix,
            plot_tfidf_matrix
        ]).tocsr()

        # Tính toán độ tương đồng Cosine trên ma trận đặc trưng tổng hợp (Chỉ tính khi cần cho movie_id, hoặc sau khi query vector được tạo)
        # Để tránh tính toán lại, chúng ta có thể đặt nó ở đây nếu nó được dùng cho cả hai trường hợp.
        # Hoặc tính toán cụ thể cho từng trường hợp để tối ưu bộ nhớ nếu dataset rất lớn.
        # Với kích thước dataset trung bình, tính toán một lần ở đây là chấp nhận được.
        cosine_sim = cosine_similarity(feature_matrix, feature_matrix)

        # Hàm trợ giúp để lấy gợi ý từ ma trận tương đồng
        def get_top_n_recommendations(sim_scores, df_movies, num_rec):
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            # Loại bỏ chính nó chỉ khi gợi ý từ một movie_id
            # Khi gợi ý từ search_keywords/user_preferences thì không loại bỏ
            # Kiểm tra xem sim_scores có phải từ một movie_id cụ thể không
            # Bổ sung một tham số is_self_exclusion vào hàm này nếu cần
            
            # Đối với movie_id, loại bỏ phần tử đầu tiên (chính nó)
            if len(sim_scores) > 0 and sim_scores[0][1] == 1.0: # Kiểm tra nếu score đầu tiên là 1.0 (chính nó)
                sim_scores = sim_scores[1:num_rec+1] 
            else: # Đối với search_keywords/user_preferences, không loại bỏ
                sim_scores = sim_scores[:num_rec]
            
            movie_indices = [i[0] for i in sim_scores]
            
            recommended_movies = []
            for i, score in zip(movie_indices, [s[1] for s in sim_scores]):
                movie = df_movies.iloc[i]
                recommended_movies.append({
                    "id": str(movie['id']),
                    "title": movie['title'],
                    "similarity": round(score, 4),
                    "genres": movie['genres'] if isinstance(movie['genres'], list) else [],
                    "plot": movie['plot'] if isinstance(movie['plot'], str) else "",
                    "fullplot": movie['fullplot'] if isinstance(movie['fullplot'], str) else "",
                    "cast": movie['cast'] if isinstance(movie['cast'], list) else [],
                    "directors": movie['directors'] if isinstance(movie['directors'], list) else [],
                    "writers": movie['writers'] if isinstance(movie['writers'], list) else [],
                    "poster": movie['poster'] if isinstance(movie['poster'], str) else "",
                    "languages": movie['languages'] if isinstance(movie['languages'], list) else [],
                    "released": movie['released'] if isinstance(movie['released'], str) else "",
                    "awards": movie['awards'] if isinstance(movie['awards'], dict) else {},
                    "lastupdated": movie['lastupdated'] if isinstance(movie['lastupdated'], str) else "",
                    "year": movie['year'] if isinstance(movie['year'], (int, float)) else None,
                    "imdb": movie['imdb'] if isinstance(movie['imdb'], dict) else {},
                    "countries": movie['countries'] if isinstance(movie['countries'], list) else [],
                    "type": movie['type'] if isinstance(movie['type'], str) else "",
                    "runtime": movie['runtime'] if isinstance(movie['runtime'], (int, float)) else None,
                })
            return recommended_movies

        if search_keywords:
            # Logic xử lý search_keywords
            query_plot_tfidf = tfidf_plot.transform([search_keywords])

            query_genres_matrix = csr_matrix((1, genres_matrix.shape[1]))
            query_cast_matrix = csr_matrix((1, cast_matrix.shape[1]))
            query_directors_matrix = csr_matrix((1, directors_matrix.shape[1]))
            query_writers_matrix = csr_matrix((1, writers_matrix.shape[1]))
            query_languages_matrix = csr_matrix((1, languages_matrix.shape[1]))
            query_countries_matrix = csr_matrix((1, countries_matrix.shape[1]))

            keywords_list = search_keywords.lower().split()
            
            matched_genres = [g for g in mlb_genres.classes_ if g.lower() in keywords_list]
            if matched_genres:
                query_genres_matrix = mlb_genres.transform([matched_genres])

            matched_cast = [c for c in mlb_cast.classes_ if c.lower() in keywords_list]
            if matched_cast:
                query_cast_matrix = mlb_cast.transform([matched_cast])

            matched_directors = [d for d in mlb_directors.classes_ if d.lower() in keywords_list]
            if matched_directors:
                query_directors_matrix = mlb_directors.transform([matched_directors])

            matched_writers = [w for w in mlb_writers.classes_ if w.lower() in keywords_list]
            if matched_writers:
                query_writers_matrix = mlb_writers.transform([matched_writers])

            matched_languages = [l for l in mlb_languages.classes_ if l.lower() in keywords_list]
            if matched_languages:
                query_languages_matrix = mlb_languages.transform([matched_languages])

            matched_countries = [c for c in mlb_countries.classes_ if c.lower() in keywords_list]
            if matched_countries:
                query_countries_matrix = mlb_countries.transform([matched_countries])

            query_feature_vector = hstack([
                query_genres_matrix,
                query_cast_matrix,
                query_directors_matrix,
                query_writers_matrix,
                query_languages_matrix,
                query_countries_matrix,
                query_plot_tfidf
            ]).tocsr()

            if query_feature_vector.shape[1] != feature_matrix.shape[1]:
                return {"error": "Lỗi: Kích thước vector tìm kiếm không khớp với ma trận đặc trưng của phim."}

            sim_scores = cosine_similarity(query_feature_vector, feature_matrix).flatten()
            sim_scores_with_indices = list(enumerate(sim_scores))
            
            top_recommendations = get_top_n_recommendations(sim_scores_with_indices, df, num_recommendations)
            
            top_recommendations = [rec for rec in top_recommendations if rec['similarity'] > 0]
            
            if not top_recommendations:
                return {"message": "Không tìm thấy gợi ý nào cho từ khóa này."}
            return {"recommendations": top_recommendations}

        elif user_preferences:
            # Logic xử lý user_preferences
            query_genres = user_preferences.get("genres", [])
            query_cast = user_preferences.get("cast", [])
            query_directors = user_preferences.get("directors", [])
            query_writers = user_preferences.get("writers", [])
            query_languages = user_preferences.get("languages", [])
            query_countries = user_preferences.get("countries", [])
            
            query_text_features = " ".join(query_genres + query_cast + query_directors + query_writers + query_languages + query_countries)
            query_plot_tfidf = tfidf_plot.transform([query_text_features])

            query_genres_matrix = mlb_genres.transform([query_genres])
            query_cast_matrix = mlb_cast.transform([query_cast])
            query_directors_matrix = mlb_directors.transform([query_directors])
            query_writers_matrix = mlb_writers.transform([query_writers])
            query_languages_matrix = mlb_languages.transform([query_languages])
            query_countries_matrix = mlb_countries.transform([query_countries])
            
            query_feature_vector = hstack([
                query_genres_matrix,
                query_cast_matrix,
                query_directors_matrix,
                query_writers_matrix,
                query_languages_matrix,
                query_countries_matrix,
                query_plot_tfidf
            ]).tocsr()

            if query_feature_vector.shape[1] != feature_matrix.shape[1]:
                return {"error": "Lỗi: Kích thước vector sở thích người dùng không khớp."}

            sim_scores = cosine_similarity(query_feature_vector, feature_matrix).flatten()
            sim_scores_with_indices = list(enumerate(sim_scores))
            
            top_recommendations = get_top_n_recommendations(sim_scores_with_indices, df, num_recommendations)
            top_recommendations = [rec for rec in top_recommendations if rec['similarity'] > 0]

            # Áp dụng các bộ lọc số học
            if 'min_year' in user_preferences and user_preferences['min_year'] is not None:
                top_recommendations = [rec for rec in top_recommendations if rec.get('year') is not None and rec.get('year', 0) >= user_preferences['min_year']]
            if 'max_year' in user_preferences and user_preferences['max_year'] is not None:
                top_recommendations = [rec for rec in top_recommendations if rec.get('year') is not None and rec.get('year', 9999) <= user_preferences['max_year']]
            if 'min_runtime' in user_preferences and user_preferences['min_runtime'] is not None:
                top_recommendations = [rec for rec in top_recommendations if rec.get('runtime') is not None and rec.get('runtime', 0) >= user_preferences['min_runtime']]
            if 'max_runtime' in user_preferences and user_preferences['max_runtime'] is not None:
                top_recommendations = [rec for rec in top_recommendations if rec.get('runtime') is not None and rec.get('runtime', 99999) <= user_preferences['max_runtime']]

            if not top_recommendations:
                return {"message": "Không tìm thấy gợi ý nào phù hợp với sở thích của bạn."}
            return {"recommendations": top_recommendations}

        elif movie_id_to_recommend:
            # Logic gợi ý theo ID phim
            try:
                obj_movie_id = ObjectId(movie_id_to_recommend)
            except Exception: # Bắt lỗi cụ thể hơn
                return {"error": "Định dạng ID phim không hợp lệ."}

            if obj_movie_id not in indices:
                return {"error": f"Không tìm thấy phim với ID: {movie_id_to_recommend} trong dữ liệu."}
            
            idx = indices[obj_movie_id]
            sim_scores = list(enumerate(cosine_sim[idx]))
            
            recommendations = get_top_n_recommendations(sim_scores, df, num_recommendations)
            return {"recommendations": recommendations}
        else:
            return {"message": "Vui lòng cung cấp 'movie_id', 'search_keywords' hoặc 'user_preferences' để nhận gợi ý."}

    except Exception as e:
        # Ghi log lỗi chi tiết hơn
        import traceback
        traceback.print_exc()
        return {"error": str(e)}
    finally:
        if client:
            client.close()

if __name__ == "__main__":
    input_data = {}
    if len(sys.argv) > 1:
        try:
            input_data = json.loads(sys.argv[1])
        except json.JSONDecodeError:
            print(json.dumps({"error": "Đầu vào JSON không hợp lệ."}))
            sys.exit(1)

    movie_id = input_data.get("movie_id")
    num_rec = input_data.get("num_recommendations", 10)
    search_keywords = input_data.get("search_keywords")
    user_preferences = input_data.get("user_preferences") # Lấy sở thích người dùng

    recommendations_result = get_recommendations(movie_id, num_rec, search_keywords, user_preferences)
    print(json.dumps(recommendations_result))