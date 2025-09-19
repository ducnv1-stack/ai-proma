# File: Dockerfile

# --- Giai đoạn 1: Build ---
    FROM node:20-slim AS builder
    WORKDIR /app
    
    # Cài đặt các dependencies
    COPY package*.json ./
    RUN npm install
    
    # Copy source code và build ứng dụng
    COPY . .
    RUN npm run build
    
    # --- Giai đoạn 2: Production ---
    FROM node:20-slim
    
    WORKDIR /app
    
    
    # Copy các file cần thiết cho production từ giai đoạn build
    # Nhờ có 'output: standalone', Next.js đã gom tất cả những gì cần thiết vào đây
    COPY --from=builder /app/public ./public
    COPY --from=builder --chown=node:node /app/.next/standalone ./
    COPY --from=builder --chown=node:node /app/.next/static ./.next/static
    
    # Chuyển sang user 'node'
    USER node
    
    EXPOSE 3000
    ENV PORT 3000
    
    # Lệnh để khởi động server Next.js đã được tối ưu
    CMD ["node", "server.js"]