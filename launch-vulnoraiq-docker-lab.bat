@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM VulnoraIQ Advanced Docker Lab launcher for Windows.
REM Prerequisite: Docker Desktop or a compatible Docker engine with Docker Compose v2.

cd /d "%~dp0"
set "WEBUI_URL=http://127.0.0.1:8787"
set "CONTAINER_NAME=vulnoraiq-web"
set "MAX_ATTEMPTS=60"

echo ============================================================
echo  VulnoraIQ Advanced Docker Lab Launcher
echo ============================================================
echo.
echo This launcher will run the full Docker Compose lab:
echo   1. Check Docker is installed and running
echo   2. Build VulnoraIQ containers
echo   3. Start Docker Compose in the background
echo   4. Wait for the WebUI health check
echo   5. Open the browser
echo.

where docker >nul 2>nul
if errorlevel 1 (
  echo Docker was not found on PATH.
  echo Install and start Docker Desktop, then run this launcher again.
  goto fail
)

docker info >nul 2>nul
if errorlevel 1 (
  echo Docker is installed but the Docker engine is not running.
  echo Start Docker Desktop and wait until it is ready, then run this launcher again.
  goto fail
)

if not exist "docker-compose.yml" (
  echo docker-compose.yml was not found in this folder.
  echo Run this launcher from the VulnoraIQ repository or release folder.
  goto fail
)

echo [1/4] Building VulnoraIQ Docker image...
docker compose build
if errorlevel 1 goto fail

echo.
echo [2/4] Starting VulnoraIQ containers...
docker compose up -d
if errorlevel 1 goto fail

echo.
echo [3/4] Current container status:
docker compose ps

echo.
echo [4/4] Waiting for VulnoraIQ WebUI to become healthy...
set /a ATTEMPT=0
:wait_loop
set /a ATTEMPT+=1
set "STATUS="
for /f "usebackq delims=" %%S in (`docker inspect --format "{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}" %CONTAINER_NAME% 2^>nul`) do set "STATUS=%%S"

if /I "!STATUS!"=="healthy" goto ready
if /I "!STATUS!"=="running" goto ready

if !ATTEMPT! GEQ %MAX_ATTEMPTS% goto timeout
if !ATTEMPT!==1 echo   Status: !STATUS!
if !ATTEMPT!==10 echo   Still waiting...
if !ATTEMPT!==20 echo   Still waiting...
if !ATTEMPT!==30 echo   Still waiting...
if !ATTEMPT!==40 echo   Still waiting...
if !ATTEMPT!==50 echo   Still waiting...
timeout /t 2 /nobreak >nul
goto wait_loop

:ready
echo.
echo VulnoraIQ WebUI is ready: %WEBUI_URL%
start "" "%WEBUI_URL%"
echo.
echo Docker containers are running in the background.
echo To stop them later, run:
echo   docker compose down
echo.
pause
exit /b 0

:timeout
echo.
echo VulnoraIQ did not become healthy in time.
echo Check logs with:
echo   docker compose logs vulnoraiq-web
echo.
goto fail

:fail
echo.
echo Startup failed.
pause
exit /b 1
