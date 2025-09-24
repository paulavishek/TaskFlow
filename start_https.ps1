# PowerShell script to start Django HTTPS development server
Write-Host "=== Django HTTPS Development Server ===" -ForegroundColor Green
Write-Host ""
Write-Host "The server will be available at: https://127.0.0.1:8000/" -ForegroundColor Yellow
Write-Host "Note: You'll need to accept the self-signed certificate warning in your browser." -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop the server." -ForegroundColor Cyan
Write-Host ""

try {
    # Activate virtual environment and start HTTPS server
    & ".\venv\Scripts\Activate.ps1"
    python manage.py runserver_plus --cert-file adhoc 127.0.0.1:8000
}
catch {
    Write-Host "Error starting HTTPS server: $_" -ForegroundColor Red
}