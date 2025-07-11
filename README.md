# CineRec - Movie suggestions

 As for the basic suggestion feature, 
                    it uses <strong>TF-IDF</strong> technique to process and calculate the similarity between 
                    keywords and sets to give the most suitable suggestion. 
                    <span className="bg-clip-text text-transparent bg-gradient-to-r from-red-500 to-purple-600 font-bold">
                        This feature is still under development in the future.</span></p>



### Basic environment variables

    MONGODB_URI=""

    PORT=
    ACCESS_TOKEN_SECRET="" 
    REFRESH_TOKEN_SECRET="" 
    
    ACCESS_TOKEN_EXPIRATION="" 
    REFRESH_TOKEN_EXPIRATION="" 


Structure-BE/

          ├── node_modules/         (Các thư viện Node.js được cài đặt)
          ├── src/                  (Thư mục chứa mã nguồn chính của ứng dụng TypeScript)
          │   ├── config/
          │   │   └── db.ts         (Cấu hình kết nối cơ sở dữ liệu, ví dụ: MongoDB)
          │   ├── controllers/
          │   │   ├── movieController.ts       (Logic xử lý các yêu cầu liên quan đến phim)
          │   │   └── preferenceMovieController.ts (Logic xử lý các yêu cầu gợi ý phim dựa trên sở thích)
          │   ├── middleware/       (Các middleware của Express)
          │   ├── ml/               (Thư mục chứa các script Machine Learning bằng Python)
          │   │   ├── movie_recommender.py       (Script Python cho việc gợi ý phim)
          │   │   └── preference_recommender.py  (Script Python cho việc gợi ý dựa trên sở thích)
          │   ├── models/
          │   │   └── Movie.ts                   (Định nghĩa schema/model Mongoose cho phim)
          │   ├── router/
          │   │   └── movieRouters.ts            (Định nghĩa các tuyến đường API liên quan đến phim)
          │   ├── services/
          │   │   └── pythonService.ts           (Service để gọi và tương tác với các script Python)
          │   ├── server.ts         (Điểm khởi đầu của ứng dụng Node.js/Express)
          │   └── swagger.ts        (Cấu hình Swagger/OpenAPI để tạo tài liệu API)
          ├── .env                  (File chứa các biến môi trường, ví dụ: chuỗi kết nối DB)
          ├── .gitignore            (File chỉ định các file/thư mục không đưa vào Git)
          ├── package-lock.json     (Ghi lại phiên bản chính xác của các dependencies)
          ├── package.json          (File cấu hình dự án Node.js, chứa scripts, dependencies)
          ├── requirements.txt      (File liệt kê các thư viện Python cần thiết)
          └── tsconfig.json         (Cấu hình TypeScript compiler)

#### Get Movies Limit

  <img width="795" height="652" alt="image" src="https://github.com/user-attachments/assets/1a91434f-cf61-4133-b191-ab87ec11a8b7" />


#### Suggestion TF-IDF By ID Movies 
  <img width="786" height="688" alt="image" src="https://github.com/user-attachments/assets/76d8f74b-32bf-4f7b-bb90-f76068b57236" />


#### Suggestion TF-IDF By Keyword
<img width="787" height="646" alt="image" src="https://github.com/user-attachments/assets/7a8501a6-59d3-4be5-bc56-7ff75b3a86b7" />

#### Suggestion TF-IDF By Interest, related
<img width="772" height="642" alt="image" src="https://github.com/user-attachments/assets/ae0f0e86-4b57-47d3-a2e7-c4671099c61b" />


### The current movie data I am using only has movies before 2024

