
import dotenv from 'dotenv';
import cors from 'cors';
dotenv.config(); 



import express, { Request, Response } from 'express';
import movieRoutes from './router/movieRouters';
import http from 'http';
import connectDB from './config/db'; 
import swaggerUi from 'swagger-ui-express'; 
import swaggerSpec from './swagger'; 

const app = express();
const server = http.createServer(app);

const PORT = process.env.PORT || 3000;

// Cấu hình CORS middleware
app.use(cors({
    origin: '*', // Cho phép mọi origin truy cập (trong môi trường phát triển)
    methods: ['GET', 'POST', 'PUT', 'DELETE'], // Các HTTP methods được cho phép
    allowedHeaders: ['Content-Type', 'Authorization'], // Các headers được cho phép
}));

app.use(express.json());

// --- KẾT NỐI MONGODB VÀ KHỞI ĐỘNG SERVER ---
connectDB() // Gọi hàm kết nối DB
    .then(() => {
        // --- Định nghĩa route gốc ---
        app.get('/', (req: Request, res: Response) => {
            res.send('Welcome to the Movie API! Access <a href="/api-docs">/api-docs</a> for API documentation.');
        });

        // --- Thiết lập Swagger UI ---
        app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerSpec));

        // --- Gắn các Movie Routes ---
        app.use('/api', movieRoutes); 


        server.listen(PORT, () => {
            console.log(`Server is running on port ${PORT}`);
            console.log(`API Docs available at http://localhost:${PORT}/api-docs`);
        });
    })
    .catch((err: any) => {
        // Lỗi kết nối DB đã được xử lý trong connectDB
        console.error('Server failed to start due to MongoDB connection error.', err);
        process.exit(1);
    });