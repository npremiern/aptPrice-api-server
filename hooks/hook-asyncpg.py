# hooks/hook-asyncpg.py 파일 생성
from PyInstaller.utils.hooks import collect_all

datas, binaries, hiddenimports = collect_all('asyncpg')