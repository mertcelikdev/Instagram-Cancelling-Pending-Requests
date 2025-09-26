@echo off
setlocal
cd /d %~dp0

:: Detect Python
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
  echo Python bulunamadi. https://www.python.org/downloads/ adresinden kurun ve tekrar deneyin.
  pause
  exit /b 1
)

:: Create venv if missing
if not exist .venv (
  echo [*] Sanal ortam olusturuluyor...
  python -m venv .venv
)

echo [*] Sanal ortam aktif ediliyor...
call .venv\Scripts\activate

echo [*] Paketler kuruluyor...
pip install --upgrade pip
pip install -r requirements.txt

echo [*] Script calisiyor...
python cancel_follow_requests.py

echo.
echo [*] Islem bitti. Sonuclar: results_cancel_follow_requests.csv
pause
