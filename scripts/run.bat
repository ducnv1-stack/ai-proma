@echo off
echo Dang khoi dong FARAMEX AI Server...
cd /d "D:\CTY-Xcelbot\ai-server-main\ai-server-main"
echo Chuyen den thu muc: %cd%
"D:\Python312\python.exe" main.py
if %errorlevel% neq 0 (
    echo Loi: Khong the chay ung dung. Hay kiem tra cac thu vien da cai dat chua.
)
pause
