@echo off
echo Dang khoi dong FARAMEX AI Server (Simple)...
cd /d "D:\CTY-Xcelbot\ai-proma\ai-proma"
echo Chuyen den thu muc: %cd%
"D:\Python312\python.exe" main_simple.py
if %errorlevel% neq 0 (
    echo Loi: Khong the chay ung dung. Hay kiem tra cac thu vien da cai dat chua.
)
pause
