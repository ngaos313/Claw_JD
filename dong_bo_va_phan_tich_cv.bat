@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul
title Dong bo JD tu GitHub va Phan tich CV ca nhan

echo ==============================================================================
echo   [DONG BO DU LIEU TU GITHUB VA PHAN TICH LO TRINH CV CA NHAN]
echo ==============================================================================
echo.

cd /d "%~dp0"

echo [1/2] Dang dong bo tin tuyen dung moi nhat tu GitHub ve may...
python run_bot.py --gap --pull
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] Co loi xay ra khi dong bo hoac phan tich.
    echo [!] Vui long kiem tra lai Python tren may.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [2/2] Dang mo Bao cao va Lo trinh phan tich ca nhan tren trinh duyet...
if exist "%~dp0local_private\reports\private_gap_analysis.html" (
    start "" "%~dp0local_private\reports\private_gap_analysis.html"
) else (
    echo [!] Khong tim thay file bao cao tai local_private\reports\private_gap_analysis.html
)

echo.
echo ==============================================================================
echo   [OK] Hoan tat! Bao cao ca nhan da duoc mo tren trinh duyet.
echo   (Toan bo CV va bao cao duoc luu tru 100%%%% rieng tu tai thu muc local_private)
echo ==============================================================================
echo.
pause
