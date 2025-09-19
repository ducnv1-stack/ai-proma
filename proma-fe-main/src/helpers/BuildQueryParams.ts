/**
 * Helper để tạo query string từ một object params.
 * Nó sẽ loại bỏ các giá trị null hoặc undefined.
 */
export const buildQueryParams = (params: Record<string, any>): string => {
  const queryParams = new URLSearchParams();
  for (const key in params) {
    if (params[key] !== null && params[key] !== undefined) {
      queryParams.append(key, String(params[key]));
    }
  }
  return queryParams.toString();
};