@echo off
setlocal enabledelayedexpansion

:: 参数解析
set architecture=%1
set build_type_char=%2
set program_name=%3

:: 设置默认值
if "%architecture%"=="" set architecture=x64
if "%build_type_char%"=="" set build_type_char=d
if "%program_name%"=="" set "program_name=%~nx%CD%"

:: 校验架构参数
if not "%architecture%"=="x64" (
    if not "%architecture%"=="x86" (
        echo 错误：架构必须是 x64 或 x86
        exit /b 1
    )
)

:: 校验构建类型
if not "%build_type_char%"=="d" (
    if not "%build_type_char%"=="r" (
        echo 错误：构建类型必须是 d 或 r
        exit /b 1
    )
)

:: 转换构建类型
if "%build_type_char%"=="d" (set build_type=Debug) else (set build_type=Release)

:: 构建目录设置
set build_dir=build\%architecture%-%build_type: =%

:: 生成器设置
set generator=MinGW Makefiles

:: 架构标志
if "%architecture%"=="x64" (set arch=-m64) else (set arch=-m32)

:: 可执行文件路径
set exe_path=%build_dir%\bin\%program_name%.exe

echo 工作目录:   %CD%
echo 构建架构:   %architecture%
echo 构建类型:   %build_type%
echo 构建目录:   %build_dir%
echo 目标程序:   %program_name%.exe
echo.

:: 创建构建目录
if not exist "%build_dir%\bin" mkdir "%build_dir%\bin"
if not exist "%build_dir%\lib" mkdir "%build_dir%\lib"

:: CMake配置
echo 正在配置CMake...
cmake -B "%build_dir%" -S . ^
    -DEXECUTABLE_OUTPUT_PATH="%build_dir%\bin" ^
    -DLIBRARY_OUTPUT_PATH="%build_dir%\lib" ^
    -DCMAKE_BUILD_TYPE=%build_type% ^
    -G "%generator%" ^
    -DCMAKE_CXX_FLAGS="%arch%" ^
    -DCMAKE_C_FLAGS="%arch%"

if %ERRORLEVEL% neq 0 (
    echo ❌ CMake配置失败
    exit /b %ERRORLEVEL%
)
echo ✅ CMake配置成功 @ %build_dir%

:: 项目构建
echo 正在构建项目...
cmake --build "%build_dir%"
if %ERRORLEVEL% neq 0 (
    echo ❌ 项目构建失败
    exit /b %ERRORLEVEL%
)
echo ✅ 项目构建成功 @ %build_dir%

:: 运行可执行文件
if not exist "%exe_path%" (
    echo ❌ 可执行文件不存在: %exe_path%
    exit /b 1
)

echo 正在运行程序...
call "%exe_path%"
if %ERRORLEVEL% neq 0 (
    echo ❌ 程序执行失败 (exit code %ERRORLEVEL%)
    exit /b %ERRORLEVEL%
)
echo ✅ 程序执行成功: %exe_path%

endlocal
exit /b 0