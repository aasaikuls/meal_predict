@echo off
echo ========================================
echo Building and Starting Docker Containers
echo ========================================
echo.

rem Read LOG_DRIVER from .env (first match, ignore inline comments)
set LOG_DRIVER=json
for /f "tokens=1,* delims==" %%a in ('findstr /b "LOG_DRIVER=" .env 2^>nul') do (
    for /f "tokens=1 delims= #" %%v in ("%%b") do set LOG_DRIVER=%%v
)

if "%LOG_DRIVER%"=="awslogs" (
    echo Log driver: awslogs ^(CloudWatch^)
    set COMPOSE_FILES=-f docker-compose.yml -f docker-compose.logging-awslogs.yml
) else (
    echo Log driver: json-file ^(local^)
    set COMPOSE_FILES=-f docker-compose.yml -f docker-compose.logging-json.yml
)

docker-compose %COMPOSE_FILES% up --build

echo.
echo ========================================
echo Containers stopped
echo ========================================
echo.
echo To start in background: docker-compose %COMPOSE_FILES% up -d
echo To view logs: docker-compose logs -f
echo To stop: docker-compose down
echo.
echo Backend: http://localhost:8001
echo Frontend: http://localhost:3001
echo ========================================
pause
