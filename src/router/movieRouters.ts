// src/routes/movieRoutes.ts
import { Router, Request, Response } from "express";
import { getMovies, getMovieRecommendations, searchMovieRecommendations } from "../controllers/movieController";
import { getPreferenceRecommendations } from "../controllers/prefernceMovieController";

const router = Router();

/**
 * @swagger
 * /movies:
 * get:
 * summary: Lấy danh sách các bộ phim với phân trang.
 * description: Truy vấn các bộ phim từ collection 'embedded_movies' và hỗ trợ phân trang.
 * parameters:
 * - in: query
 * name: page
 * schema:
 * type: integer
 * default: 1
 * description: Số trang mong muốn (bắt đầu từ 1).
 * - in: query
 * name: limit
 * schema:
 * type: integer
 * default: 10
 * description: Số lượng phim trên mỗi trang (tối đa 100).
 * responses:
 * 200:
 * description: Danh sách các bộ phim và thông tin phân trang.
 * content:
 * application/json:
 * schema:
 * type: object
 * properties:
 * movies:
 * type: array
 * items:
 * $ref: '#/components/schemas/Movie' # Tham chiếu đến Schema Movie
 * currentPage:
 * type: integer
 * example: 1
 * totalPages:
 * type: integer
 * example: 100
 * totalResults:
 * type: integer
 * example: 1000
 * resultsPerPage:
 * type: integer
 * example: 10
 * 400:
 * description: Yêu cầu không hợp lệ (ví dụ: limit là số âm).
 * 500:
 * description: Lỗi máy chủ nội bộ.
 */
router.get("/movies", getMovies as (req: Request, res: Response) => Promise<void>);


/**
 * @swagger
 * /movies/recommend/{id}:
 * get:
 * summary: Gợi ý các bộ phim tương tự.
 * description: Trả về danh sách các bộ phim có nội dung tương tự dựa trên ID phim được cung cấp.
 * parameters:
 * - in: path
 * name: id
 * required: true
 * schema:
 * type: string
 * description: ID của bộ phim cơ sở để tìm gợi ý (ví dụ: ObjectId từ MongoDB).
 * example: "573a1391f29313caabcd8828"
 * - in: query
 * name: num_rec
 * schema:
 * type: integer
 * default: 10
 * description: Số lượng phim gợi ý muốn nhận.
 * responses:
 * 200:
 * description: Danh sách các phim được gợi ý.
 * content:
 * application/json:
 * schema:
 * type: object
 * properties:
 * recommendations:
 * type: array
 * items:
 * type: object
 * properties:
 * id:
 * type: string
 * example: "573a1391f29313caabcd8829"
 * title:
 * type: string
 * example: "The Maltese Falcon"
 * similarity:
 * type: number
 * format: float
 * example: 0.8543
 * 400:
 * description: ID phim không hợp lệ hoặc không được cung cấp, hoặc lỗi từ script Python.
 * 500:
 * description: Lỗi máy chủ nội bộ hoặc lỗi khi chạy script Python.
 */
router.get("/movies/recommend/:id", getMovieRecommendations as (req: Request, res: Response) => Promise<void>);

router.get('/movies/search', searchMovieRecommendations as (req: Request, res: Response) => Promise<void>);

router.get('/movies/preference-recommendations', getPreferenceRecommendations as (req: Request, res: Response) => Promise<void>);

 

export default router;