# preference_recommender.py

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import hstack, csr_matrix
from pymongo import MongoClient
import os
import json
import argparse
import sys

# --- MongoDB connection settings ---
MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = MONGODB_URI.split('/')[-1].split('?')[0] 

# --- GLOBAL MODEL OBJECTS ---
tfidf_plot = None
mlbs = {}
feature_matrix_shape = None
cached_feature_matrix_pref = None

def load_and_prepare_data():
    """
    Loads movie data from MongoDB and performs initial preprocessing.
    Returns: df (DataFrame)
    """
    client = None
    try:
        client = MongoClient(MONGODB_URI)
        db = client[DB_NAME]
        movies_collection = db['embedded_movies']

        movies_data = list(movies_collection.find({}, {
            '_id': 1, 'title': 1, 'plot': 1, 'genres': 1, 'cast': 1, 
            'directors': 1, 'writers': 1, 'languages': 1, 'countries': 1, 'year': 1, 'poster': 1
        }))
        
        if not movies_data:
            print("Không có dữ liệu phim trong MongoDB để tạo gợi ý.", file=sys.stderr)
            raise ValueError("Không có dữ liệu phim trong MongoDB để tạo gợi ý.")

        df = pd.DataFrame(movies_data)
        df['id'] = df['_id']
        
        for col in ['genres', 'cast', 'directors', 'writers', 'languages', 'countries']:
            df[col] = df[col].apply(lambda x: [str(item).strip().replace(" ", "") for item in x] if isinstance(x, list) else [])
        df['plot'] = df['plot'].fillna('')
        df['year'] = pd.to_numeric(df['year'], errors='coerce')
        
        # --- THAY ĐỔI MỚI: Xử lý giá trị NaN trong DataFrame thành None ---
        # Điều này rất quan trọng để tránh lỗi JSON.parse ở phía Node.js
        df = df.replace({np.nan: None}) # Thay thế np.nan bằng None
        
        return df

    except Exception as e:
        print(f"Lỗi khi tải hoặc tiền xử lý dữ liệu: {e}", file=sys.stderr)
        raise
    finally:
        if client:
            client.close()

def load_or_train_models_and_matrix(df):
    """
    Loads or trains TF-IDF and MLB models and computes the full feature matrix.
    This runs once per script execution (or on first call if cached).
    """
    global tfidf_plot, mlbs, feature_matrix_shape, cached_feature_matrix_pref
    
    if tfidf_plot is not None and mlbs and feature_matrix_shape is not None and cached_feature_matrix_pref is not None:
        print("Models and feature matrix already loaded/cached for preference_recommender.", file=sys.stderr)
        return cached_feature_matrix_pref

    print("Training/Loading models and feature matrix for preference_recommender...", file=sys.stderr)
    
    tfidf_plot = TfidfVectorizer(stop_words='english', min_df=5, max_df=0.8)
    plot_tfidf_matrix = tfidf_plot.fit_transform(df['plot'])

    current_sparse_matrices = []
    
    for col in ['genres', 'cast', 'directors', 'writers', 'languages', 'countries']:
        mlb = MultiLabelBinarizer()
        encoded_col = mlb.fit_transform(df[col])
        mlbs[col] = mlb
        current_sparse_matrices.append(encoded_col)
    
    current_sparse_matrices.append(plot_tfidf_matrix)
    
    combined_matrix = hstack(current_sparse_matrices).tocsr()
    feature_matrix_shape = combined_matrix.shape[1]
    
    cached_feature_matrix_pref = combined_matrix
    print(f"Models and feature matrix trained. Shape: {feature_matrix_shape}", file=sys.stderr)
    
    return combined_matrix

# Helper function to get recommendations from similarity scores
def get_top_n_recommendations(sim_scores_array, df_movies, num_rec, min_year_filter=None, max_year_filter=None):
    sim_scores_with_indices = list(enumerate(sim_scores_array))
    sim_scores_with_indices = sorted(sim_scores_with_indices, key=lambda x: x[1], reverse=True)
    
    recommended_movies = []
    for i, score in sim_scores_with_indices:
        if score <= 0:
            continue

        movie = df_movies.iloc[i]
        
        movie_year = movie.get('year')
        if min_year_filter is not None and movie_year is not None and movie_year < min_year_filter:
            continue
        if max_year_filter is not None and movie_year is not None and movie_year > max_year_filter:
            continue

        # --- THAY ĐỔI CŨNG QUAN TRỌNG: Đảm bảo giá trị "poster" được xử lý thành None nếu là NaN ---
        # Mặc dù đã xử lý np.nan ở load_and_prepare_data, nhưng đây là một lớp bảo vệ nữa
        poster_value = movie.get('poster')
        if isinstance(poster_value, float) and np.isnan(poster_value):
            poster_value = None

        recommended_movies.append({
            "id": str(movie['id']),
            "title": movie['title'],
            "similarity": round(score, 4),
            "genres": movie.get('genres', []),
            "plot": movie.get('plot', ''),
            "cast": movie.get('cast', []),
            "directors": movie.get('directors', []),
            "writers": movie.get('writers', []),
            "poster": poster_value, # Sử dụng giá trị đã được xử lý
            "languages": movie.get('languages', []),
            "year": movie.get('year'),
            "countries": movie.get('countries', [])
        })
        if len(recommended_movies) >= num_rec:
            break

    return recommended_movies

def get_preference_recommendations(num_recommendations=10, genres=None, cast=None, directors=None, writers=None, 
                                   languages=None, countries=None, min_year=None, max_year=None):
    try:
        df = load_and_prepare_data()
        feature_matrix = load_or_train_models_and_matrix(df)

        query_parts = []
        
        for col in ['genres', 'cast', 'directors', 'writers', 'languages', 'countries']:
            pref_list_str = None
            if col == 'genres': pref_list_str = genres
            elif col == 'cast': pref_list_str = cast
            elif col == 'directors': pref_list_str = directors
            elif col == 'writers': pref_list_str = writers
            elif col == 'languages': pref_list_str = languages
            elif col == 'countries': pref_list_str = countries
            
            if pref_list_str:
                pref_list = [str(item).strip().replace(" ", "") for item in pref_list_str.split(',')]
                query_parts.append(mlbs[col].transform([pref_list]))
            else:
                query_parts.append(csr_matrix((1, len(mlbs[col].classes_))))

        plot_vocab_size = len(tfidf_plot.vocabulary_) if hasattr(tfidf_plot, 'vocabulary_') else 0
        query_parts.append(csr_matrix((1, plot_vocab_size)))

        query_feature_vector = hstack(query_parts).tocsr()

        if query_feature_vector.shape[1] != feature_matrix_shape:
            missing_cols = feature_matrix_shape - query_feature_vector.shape[1]
            if missing_cols > 0:
                query_feature_vector = hstack([query_feature_vector, csr_matrix((1, missing_cols))]).tocsr()
            elif missing_cols < 0:
                error_msg = f"Lỗi nội bộ: Kích thước vector sở thích ({query_feature_vector.shape[1]}) lớn hơn ma trận đặc trưng dự kiến ({feature_matrix_shape})."
                print(error_msg, file=sys.stderr)
                return {"error": error_msg}

        if query_feature_vector.nnz == 0:
            return {"message": "Vui lòng nhập ít nhất một tiêu chí sở thích để nhận gợi ý."}

        sim_scores = cosine_similarity(query_feature_vector, feature_matrix).flatten()
        
        top_recommendations = get_top_n_recommendations(
            sim_scores, df, num_recommendations, min_year_filter=min_year, max_year_filter=max_year
        )
        
        if not top_recommendations:
            return {"message": "Không tìm thấy gợi ý nào phù hợp với sở thích của bạn."}
        return {"recommendations": top_recommendations}

    except Exception as e:
        print(f"Lỗi trong get_preference_recommendations: {e}", file=sys.stderr)
        return {"error": f"Lỗi nội bộ của hệ thống gợi ý theo sở thích: {e}"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get movie recommendations based on preferences.")
    parser.add_argument('json_input', type=str, 
                        help='A JSON string containing all input parameters for recommendation.')
    
    args = parser.parse_args()

    try:
        input_params = json.loads(args.json_input)

        num_rec = input_params.get('num_recommendations', 10)
        genres = input_params.get('genres')
        cast = input_params.get('cast')
        directors = input_params.get('directors')
        writers = input_params.get('writers')
        languages = input_params.get('languages')
        countries = input_params.get('countries')
        min_year = input_params.get('min_year')
        max_year = input_params.get('max_year')

        result = get_preference_recommendations(
            num_recommendations=num_rec,
            genres=genres,
            cast=cast,
            directors=directors,
            writers=writers,
            languages=languages,
            countries=countries,
            min_year=min_year,
            max_year=max_year
        )
        print(json.dumps(result))
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Lỗi phân tích cú pháp JSON đầu vào: {e}"}), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": f"Lỗi không xác định khi xử lý yêu cầu: {e}"}), file=sys.stderr)
        sys.exit(1)