@ECHO OFF
:: This batch file builds a Windows binary executable
ECHO =======================================================
ECHO iRacing Safety Car Generator - Windows Build Script
ECHO =======================================================

:: Check if Python is installed
WHERE python >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    ECHO Python is not installed or not in PATH. Please install Python 3.x.
    PAUSE
    EXIT /B 1
)

:: Parse command line arguments
SET VERSION=
SET ZIP=
SET CLEAN_ONLY=

:PARSE_ARGS
IF "%~1"=="" GOTO END_PARSE_ARGS
IF /I "%~1"=="--version" SET VERSION=--version %~2 & SHIFT & SHIFT & GOTO PARSE_ARGS
IF /I "%~1"=="-v" SET VERSION=--version %~2 & SHIFT & SHIFT & GOTO PARSE_ARGS
IF /I "%~1"=="--zip" SET ZIP=--zip & SHIFT & GOTO PARSE_ARGS
IF /I "%~1"=="-z" SET ZIP=--zip & SHIFT & GOTO PARSE_ARGS
IF /I "%~1"=="--clean-only" SET CLEAN_ONLY=--clean-only & SHIFT & GOTO PARSE_ARGS
SHIFT
GOTO PARSE_ARGS

:END_PARSE_ARGS

:: Run the Python build script
ECHO Running build script...
python build.py %VERSION% %ZIP% %CLEAN_ONLY%

IF %ERRORLEVEL% NEQ 0 (
    ECHO Build failed with error code %ERRORLEVEL%
    PAUSE
    EXIT /B %ERRORLEVEL%
)

ECHO Build completed successfully!
ECHO See the 'dist' directory for the executable and necessary files.
PAUSE