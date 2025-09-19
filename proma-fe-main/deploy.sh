#!/bin/bash
set -e

echo "--- Bắt đầu triển khai Famarex Frontend ---"

# 1. Cập nhật phiên bản mới nhất từ Git
echo ">>> Đang cập nhật repo từ GitHub..."
git pull

# 2. Build và khởi chạy lại các container
echo ">>> Đang build và khởi chạy lại các container..."
# --build: Bắt buộc build lại image nếu có thay đổi trong code hoặc Dockerfile
# -d: Chạy ở chế độ nền
# --force-recreate: Đảm bảo container được tạo lại
docker compose up --build -d --force-recreate

# 3. Dọn dẹp các image cũ không còn sử dụng
echo ">>> Đang dọn dẹp các image cũ..."
docker image prune -af

echo "--- Hoàn tất triển khai! ---"