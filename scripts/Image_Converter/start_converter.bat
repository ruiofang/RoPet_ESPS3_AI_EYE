@echo off
echo RoPet Image Converter Tools
echo =========================
echo.
echo 1. H文件转PNG图片工具
echo 2. PNG图片转H文件工具 (逆向)
echo 3. 退出
echo.
set /p choice="请选择要运行的工具 (1-3): "

if "%choice%"=="1" (
    echo 启动 H文件转PNG工具...
    python h_to_png_converter.py
) else if "%choice%"=="2" (
    echo 启动 PNG转H文件工具...
    python png_to_h_converter.py
) else if "%choice%"=="3" (
    echo 退出程序...
    exit
) else (
    echo 无效选择，请重新运行程序
    pause
)

pause
