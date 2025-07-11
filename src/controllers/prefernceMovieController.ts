// src/controllers/movieController.ts

import { Request, Response } from 'express';
import { runPythonScript } from '../services/pythonService';

export const getPreferenceRecommendations = async (req: Request, res: Response) => {
    const {
        num_rec,
        genres,
        cast,
        directors,
        writers,
        languages,
        countries,
        min_year,
        max_year
    } = req.query;

    const numRecommendations = parseInt(num_rec as string) || 10;
    // Chuyển đổi năm sang số, nếu không có thì là undefined
    const minYear = min_year ? parseInt(min_year as string) : undefined;
    const maxYear = max_year ? parseInt(max_year as string) : undefined;

    // Chuẩn bị dữ liệu đầu vào cho script Python
    // Các trường chỉ được thêm vào nếu chúng có giá trị
    const inputData: { [key: string]: any } = {
        num_recommendations: numRecommendations
    };

    if (genres) inputData.genres = genres as string;
    if (cast) inputData.cast = cast as string;
    if (directors) inputData.directors = directors as string;
    if (writers) inputData.writers = writers as string;
    if (languages) inputData.languages = languages as string;
    if (countries) inputData.countries = countries as string;
    if (minYear !== undefined) inputData.min_year = minYear;
    if (maxYear !== undefined) inputData.max_year = maxYear;

    // Kiểm tra xem có ít nhất một tiêu chí sở thích được cung cấp không
    // (ngoại trừ num_recommendations)
    const hasPreferences = Object.keys(inputData).some(key =>
        key !== 'num_recommendations' && inputData[key] !== undefined
    );

    if (!hasPreferences) {
        return res.status(400).json({ message: "Vui lòng nhập ít nhất một tiêu chí sở thích để nhận gợi ý." });
    }

    try {
        // Gọi script Python preference_recommender.py thông qua service
        const result = await runPythonScript('preference_recommender.py', inputData);

        // Xử lý kết quả từ script Python
        if (result.error) {
            // Nếu script Python trả về lỗi, gửi lỗi đó cho client
            return res.status(400).json({ message: result.error });
        }
        // Gửi kết quả thành công cho client
        res.json(result);
    } catch (error: any) {
        // Bắt lỗi nếu có vấn đề trong quá trình chạy script Python
        console.error("Lỗi trong getPreferenceRecommendations:", error);
        // runPythonScript đã định dạng lỗi, chỉ cần trả về nó
        res.status(500).json(error);
    }
};