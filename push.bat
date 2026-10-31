@echo off
REM Push this folder to your GitHub repo. Double-click this file, or run push.bat
REM It asks for your repo link, e.g. https://github.com/YOURNAME/reel-factory.git
set /p REPO=Paste your GitHub repo link:
if "%REPO%"=="" echo No link given. Stopping. & pause & exit /b 1
git init -b main
git add .
git commit -m "Reel factory: topic or script in, Hindi reel out"
git remote remove origin 2>nul
git remote add origin %REPO%
git push -u origin main
echo Done. Refresh your repo page on GitHub to check the files are there.
pause
