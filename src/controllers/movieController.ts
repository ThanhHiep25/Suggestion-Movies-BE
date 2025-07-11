// src/controllers/movieController.ts

import { Request, Response } from 'express';
import Movie from '../models/Movie';
import { runPythonScript } from '../services/pythonService'; // Import hàm từ service

// Hàm xử lý việc lấy danh sách phim (không thay đổi)
export const getMovies = async (req: Request, res: Response) => {
    try {
        const page = parseInt(req.query.page as string) || 1;
        const limit = parseInt(req.query.limit as string) || 10;

        const actualLimit = Math.min(limit, 100);
        if (actualLimit <= 0) {
            return res.status(400).json({ message: "Limit phải là số dương." });
        }

        const skip = (page - 1) * actualLimit;
        if (skip < 0) {
            return res.status(400).json({ message: "Page phải là số dương." });
        }

        const movies = await Movie.find()
                                .skip(skip)
                                .limit(actualLimit);

        const totalMovies = await Movie.countDocuments();

        res.json({
            movies,
            currentPage: page,
            totalPages: Math.ceil(totalMovies / actualLimit),
            totalResults: totalMovies,
            resultsPerPage: actualLimit
        });
    } catch (error: any) {
        console.error("Lỗi khi lấy danh sách phim:", error);
        res.status(500).json({ message: "Đã xảy ra lỗi khi lấy danh sách phim." });
    }
};

// Hàm xử lý việc lấy gợi ý phim theo ID
export const getMovieRecommendations = async (req: Request, res: Response) => {
    const { id } = req.params;
    const numRecommendations = parseInt(req.query.num_rec as string) || 10;

    if (!id) {
        return res.status(400).json({ message: "Vui lòng cung cấp ID phim để nhận gợi ý." });
    }

    try {
        // Gọi hàm từ service
        const result = await runPythonScript('movie_recommender.py', {
            movie_id: id,
            num_recommendations: numRecommendations
        });

        if (result.error) {
            return res.status(400).json({ message: result.error });
        }
        res.json(result);
    } catch (error: any) {
        console.error("Lỗi trong getMovieRecommendations:", error);
        res.status(500).json(error); // Trả về lỗi đã được định dạng từ hàm runPythonScript
    }
};

// Hàm xử lý việc lấy gợi ý phim theo từ khóa tìm kiếm
export const searchMovieRecommendations = async (req: Request, res: Response) => {
    const { keywords } = req.query;
    const numRecommendations = parseInt(req.query.num_rec as string) || 10;

    if (!keywords || typeof keywords !== 'string' || keywords.trim() === '') {
        return res.status(400).json({ message: "Vui lòng cung cấp từ khóa tìm kiếm." });
    }

    try {
        // Gọi hàm từ service
        const result = await runPythonScript('movie_recommender.py', {
            search_keywords: keywords,
            num_recommendations: numRecommendations
        });

        if (result.error) {
            return res.status(400).json({ message: result.error });
        }
        res.json(result);
    } catch (error: any) {
        console.error("Lỗi trong searchMovieRecommendations:", error);
        res.status(500).json(error); // Trả về lỗi đã được định dạng từ hàm runPythonScript
    }
};
