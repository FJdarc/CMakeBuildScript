@echo off
setlocal enabledelayedexpansion

rem Check for help requests in any parameter position
set HELP_REQUESTED=0
for %%A in (%*) do (
    if /i "%%~A"=="-h" set HELP_REQUESTED=1
    if /i "%%~A"=="--help" set HELP_REQUESTED=1
)
if %HELP_REQUESTED% equ 1 (
    call :ShowUsage
    exit /b 0
)

rem Validate parameter count
if not "%3"=="" (
    echo Error: Too many parameters.
    call :ShowUsage
    exit /b 1
)

rem Initialize build configuration
if "%1"=="" (
    set BUILD_TYPE=Debug
    set "BUILD_DIR=C:/dev/OpenGL/out/debug"
    set "EXEC_PATH=C:/dev/OpenGL/out/debug/bin"
) else if /i "%1"=="d" (
    set BUILD_TYPE=Debug
    set "BUILD_DIR=C:/dev/OpenGL/out/debug"
    set "EXEC_PATH=C:/dev/OpenGL/out/debug/bin"
) else if /i "%1"=="r" (
    set BUILD_TYPE=Release
    set "BUILD_DIR=C:/dev/OpenGL/out/release"
    set "EXEC_PATH=C:/dev/OpenGL/out/release/bin"
) else (
    echo Error: Invalid build type "%1"
    call :ShowUsage
    exit /b 1
)

rem Set executable name
if "%2"=="" (
    set "PROGRAM_NAME=OpenGL.exe"
) else (
    set "PROGRAM_NAME=%~n2.exe"
)

rem Create build directories
for %%D in ("%BUILD_DIR%" "%EXEC_PATH%") do (
    if not exist "%%~D" (
        mkdir "%%~D" >nul 2>&1
        if errorlevel 1 (
            echo Error: Failed to create directory "%%~D"
            exit /b 1
        )
    )
)

rem CMake configuration
echo Configuring CMake (%BUILD_TYPE%)...
cmake -B "%BUILD_DIR%" -S . -G "MinGW Makefiles" ^
    -DEXECUTABLE_OUTPUT_PATH="%EXEC_PATH%" ^
    -DLIBRARY_OUTPUT_PATH="%EXEC_PATH%" ^
    -DCMAKE_BUILD_TYPE=%BUILD_TYPE%

if %ERRORLEVEL% neq 0 (
    echo CMake configuration failed!
    exit /b %ERRORLEVEL%
)
echo CMake configuration successful!

rem Build project
echo Building project...
cmake --build "%BUILD_DIR%"

if %ERRORLEVEL% neq 0 (
    echo Build failed!
    exit /b %ERRORLEVEL%
)
echo Project built successfully!

rem Run program
if not exist "%EXEC_PATH%/%PROGRAM_NAME%" (
    echo Error: Executable not found "%EXEC_PATH%/%PROGRAM_NAME%"
    exit /b 1
)

echo Launching program...
start "" /D "%EXEC_PATH%" "%PROGRAM_NAME%"

exit /b 0

:ShowUsage
echo Usage: %~n0 [build_type] [executable_name] [options]
echo.
echo Arguments:
echo   build_type       d=Debug, r=Release (default: Debug)
echo   executable_name  Output filename without extension (default: OpenGL)
echo.
echo Options:
echo   -h, --help       Show this help message
echo.
echo Examples:
echo   %~n0               Debug build with OpenGL.exe
echo   %~n0 r MyApp       Release build with MyApp.exe
echo   %~n0 --help        Show this help message
exit /b 0