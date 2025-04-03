@echo off
pyinstaller --onefile --name api_server main.py
#echo EXE 파일이 생성되었습니다: dist/api_server.exe
pause
