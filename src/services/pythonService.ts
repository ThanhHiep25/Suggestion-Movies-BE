// src/services/pythonService.ts

import { spawn } from 'child_process';
import path from 'path';

/**
 * Hàm trợ giúp để chạy script Python và trả về kết quả.
 * @param scriptName Tên của file script Python (ví dụ: 'movie_recommender.py').
 * @param inputData Dữ liệu đầu vào sẽ được gửi tới script Python dưới dạng JSON.
 * @returns Promise chứa kết quả từ script Python hoặc lỗi.
 */
export async function runPythonScript(scriptName: string, inputData: any): Promise<any> {
    const pythonScriptFileName = scriptName;
    let pythonScriptDirPath: string;

    // Xác định đường dẫn thư mục của script Python dựa trên môi trường
    // __dirname ở đây là đường dẫn đến thư mục 'services'
    if (process.env.NODE_ENV === 'production') {
        // Trong môi trường production, project_root/dist/services -> project_root/dist/ml
        pythonScriptDirPath = path.join(__dirname, '..', '..', 'dist', 'ml');
    } else {
        // Trong môi trường development, project_root/src/services -> project_root/src/ml
        pythonScriptDirPath = path.join(__dirname, '..', 'ml');
    }

    const pythonScriptPath = path.join(pythonScriptDirPath, pythonScriptFileName);
    const inputJsonString = JSON.stringify(inputData);
    const pythonCommand = process.platform === 'win32' ? 'python' : 'python3';

    return new Promise((resolve, reject) => {
        let pythonProcessOutput = '';
        let pythonProcessError = '';

        console.log(`[PythonService] Đang thực hiện lệnh chạy Python script từ: ${pythonScriptPath}`);
        console.log(`[PythonService] Lệnh Python: ${pythonCommand}`);

        const python = spawn(pythonCommand, [pythonScriptPath, inputJsonString], {
            env: {
                ...process.env,
                // Đảm bảo MONGODB_URI được truyền vào tiến trình Python
                MONGODB_URI: process.env.MONGODB_URI,
                DB_NAME: process.env.DB_NAME // Truyền thêm DB_NAME nếu cần
            }
        });

        python.stdout.on('data', (data) => {
            pythonProcessOutput += data.toString();
        });

        python.stderr.on('data', (data) => {
            pythonProcessError += data.toString();
            console.error(`[PythonService] Python Stderr: ${data.toString()}`);
        });

        python.on('close', (code) => {
            if (code !== 0) {
                console.error(`[PythonService] Python script exited with code ${code}`);
                console.error(`[PythonService] Python Error Output: ${pythonProcessError}`);
                return reject({
                    message: "Lỗi khi chạy script Python.",
                    error: pythonProcessError || "Không có lỗi cụ thể từ Python."
                });
            }

            try {
                const result = JSON.parse(pythonProcessOutput);
                resolve(result);
            } catch (parseError: any) {
                console.error("[PythonService] Lỗi khi phân tích cú pháp JSON từ Python:", parseError);
                console.error(`[PythonService] Python Raw Output: ${pythonProcessOutput}`);
                reject({
                    message: "Lỗi nội bộ khi xử lý kết quả từ Python.",
                    error: parseError.message
                });
            }
        });

        python.on('error', (err) => {
            console.error("[PythonService] Failed to start Python process:", err);
            let errorMessage = "Không thể khởi động tiến trình Python. Vui lòng đảm bảo Python đã được cài đặt và nằm trong biến môi trường PATH của hệ thống.";
            if ((err as any).code === 'ENOENT') {
                errorMessage += " Lỗi ENOENT: Hệ thống không tìm thấy lệnh 'python' hoặc 'python3'.";
                errorMessage += " Hãy thử gõ 'python --version' hoặc 'python3 --version' trong terminal mới để kiểm tra.";
            }
            reject({
                message: errorMessage,
                error: err.message
            });
        });
    });
}