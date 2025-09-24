@echo off
echo Starting Django HTTPS Development Server...
echo.
echo The server will be available at: https://127.0.0.1:8000/
echo Note: You'll need to accept the self-signed certificate warning in your browser.
echo.
echo Press Ctrl+C to stop the server.
echo.

REM Activate virtual environment and start HTTPS server
call .\venv\Scripts\activate.bat
python manage.py runserver_plus --cert-file adhoc 127.0.0.1:8000