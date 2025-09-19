// file: lib/ApiError.ts

/**
 * Lớp lỗi tùy chỉnh để biểu diễn các lỗi trả về từ API.
 * Nó chứa mã trạng thái HTTP và nội dung phản hồi lỗi từ server.
 */
export class ApiError extends Error {
    /**
     * Mã trạng thái HTTP (ví dụ: 400, 404, 500).
     */
    public readonly status: number;
    
    /**
     * Nội dung chi tiết của lỗi trả về từ server.
     * Đây có thể là một chuỗi hoặc một đối tượng JSON.
     */
    public readonly body: any;
  
    /**
     * @param status - Mã trạng thái HTTP.
     * @param statusText - Chuỗi trạng thái HTTP (ví dụ: 'Bad Request').
     * @param body - Nội dung phản hồi từ server.
     * @param message - Một thông điệp lỗi tùy chỉnh. Nếu không được cung cấp, một thông điệp mặc định sẽ được tạo.
     */
    constructor(status: number, statusText: string, body: any, message?: string) {
      // Gọi constructor của lớp cha (Error) với một thông điệp lỗi rõ ràng.
      super(message || `Request failed with status ${status} ${statusText}`);
  
      // Đặt tên cho class lỗi, hữu ích cho việc debugging.
      this.name = 'ApiError';
  
      // Gán các thuộc tính tùy chỉnh.
      this.status = status;
      this.body = body;
  
      // Đảm bảo prototype chain hoạt động chính xác (quan trọng cho instanceof).
      Object.setPrototypeOf(this, ApiError.prototype);
    }
  }