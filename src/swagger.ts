// src/swagger.ts
import swaggerJsdoc from 'swagger-jsdoc';

const PORT = process.env.PORT || 3000; // Đảm bảo PORT được lấy từ process.env

// Cấu hình Swagger JSDoc options
const swaggerOptions = {
    definition: {
        openapi: '3.0.0', // Phiên bản OpenAPI Specification
        info: {
            title: 'Movie API with Pagination', // Tiêu đề API của bạn
            version: '1.0.0', // Phiên bản API của bạn
            description: 'API để truy vấn và quản lý danh sách phim từ MongoDB.', // Mô tả API
        },
        servers: [ // Định nghĩa các server nơi API được triển khai
            {
                url: `http://localhost:${PORT}`, // URL cơ sở của API
                description: 'Local Development Server',
            },
        ],
        components: { // Định nghĩa các schema để tham chiếu trong các route
            schemas: {
                // Định nghĩa Schema cho Movie để Swagger UI hiển thị cấu trúc của đối tượng Movie
                Movie: {
                    type: 'object',
                    properties: {
                        _id: { type: 'string', description: 'ID duy nhất của bộ phim.', example: '60c72b2f9f1b2c001c8e4d6a' },
                        plot: { type: 'string', description: 'Tóm tắt cốt truyện của phim.', example: 'A brave young man leads an expedition to the lost city of Opar.' },
                        genres: { type: 'array', items: { type: 'string' }, description: 'Thể loại của phim.', example: ['Action', 'Adventure'] },
                        runtime: { type: 'integer', description: 'Thời lượng phim bằng phút.', example: 100 },
                        rated: { type: 'string', description: 'Xếp hạng phim (ví dụ: PG, G).', example: 'G' },
                        cast: { type: 'array', items: { type: 'string' }, description: 'Danh sách diễn viên chính.', example: ['Johnny Weissmuller', 'Maureen O\'Sullivan'] },
                        poster: { type: 'string', description: 'URL của poster phim.', example: 'https://m.media-amazon.com/images/M/MV5BNjVBNjkwYTEwMDY3OTc4NDY0YjE1Mi5BMl5BanBnXkFtZTgwNTU5MTYxMzI@._V1_SX300.jpg' },
                        title: { type: 'string', description: 'Tiêu đề của phim.', example: 'Tarzan the Ape Man' },
                        fullplot: { type: 'string', description: 'Toàn bộ cốt truyện của phim.', example: 'James Parker and Harry Holt are on an expedition in Africa...' },
                        languages: { type: 'array', items: { type: 'string' }, description: 'Ngôn ngữ của phim.', example: ['English'] },
                        released: { type: 'string', format: 'date-time', description: 'Ngày phát hành phim.', example: '1932-04-02T08:00:00.000+00:00' },
                        directors: { type: 'array', items: { type: 'string' }, description: 'Đạo diễn của phim.', example: ['W.S. Van Dyke'] },
                        writers: { type: 'array', items: { type: 'string' }, description: 'Biên kịch của phim.', example: ['Cyril Hume', 'Ivor Novello'] },
                        awards: {
                            type: 'object',
                            properties: {
                                wins: { type: 'integer', example: 1 },
                                nominations: { type: 'integer', example: 0 },
                                text: { type: 'string', example: '1 win.' }
                            }
                        },
                        lastupdated: { type: 'string', format: 'date-time', description: 'Lần cuối cùng cập nhật thông tin phim.', example: '2015-09-01T00:05:45.413000000Z' },
                        year: { type: 'integer', example: 1932 },
                        imdb: {
                            type: 'object',
                            properties: {
                                rating: { type: 'number', format: 'float', example: 7.8 },
                                votes: { type: 'integer', example: 948 },
                                id: { type: 'integer', example: 23117 }
                            }
                        },
                        countries: { type: 'array', items: { type: 'string' }, example: ['USA'] },
                        type: { type: 'string', example: 'movie' },
                        tomatoes: {
                            type: 'object',
                            properties: {
                                viewer: {
                                    type: 'object',
                                    properties: {
                                        rating: { type: 'number', format: 'float', example: 3.5 },
                                        numReviews: { type: 'integer', example: 948 },
                                        meter: { type: 'integer', example: 69 }
                                    }
                                },
                                dvd: { type: 'string', format: 'date-time', example: '2004-04-20T00:00:00.000Z' },
                                critic: {
                                    type: 'object',
                                    properties: {
                                        rating: { type: 'number', format: 'float', example: 7.8 },
                                        numReviews: { type: 'integer', example: 13 },
                                        meter: { type: 'integer', example: 100 }
                                    }
                                },
                                lastUpdated: { type: 'string', format: 'date-time', example: '2015-09-12T18:54:59.000Z' },
                                rotten: { type: 'integer', example: 8 },
                                production: { type: 'string', example: 'MGM Home Entertainment' },
                                fresh: { type: 'integer', example: 13 }
                            }
                        },
                        num_mflix_comments: { type: 'integer', example: 0 }
                    }
                }
            }
        }
    },
    apis: ['./router/*.ts'],
};

// Khởi tạo swagger-jsdoc để tạo ra spec OpenAPI
const swaggerSpec = swaggerJsdoc(swaggerOptions);

export default swaggerSpec;