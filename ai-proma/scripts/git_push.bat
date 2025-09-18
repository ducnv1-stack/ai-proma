@echo off
echo ========================================
echo          PROMA GIT PUSH SCRIPT
echo ========================================
echo.

echo [1/4] Checking Git status...
git status

echo.
echo [2/4] Adding all changes to staging area...
git add .

echo.
echo [3/4] Committing changes...
git commit -m "Update Proma AI Project Manager - OpenRouter integration, authentication system, and UI improvements"

echo.
echo [4/4] Pushing to remote repository...
git push

echo.
echo ========================================
echo          PUSH COMPLETED!
echo ========================================
pause
