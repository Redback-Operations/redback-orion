$root = $PSScriptRoot

Write-Host "========================================"
Write-Host " Starting Orion Services"
Write-Host "========================================"

# --------------------------------------------------
# Player Service - Port 8080
# --------------------------------------------------

Write-Host "`nStarting Player Service (port 8080)..."

Start-Process `
    -FilePath "python" `
    -ArgumentList "-m uvicorn main:app --host 0.0.0.0 --port 8080" `
    -WorkingDirectory "$root\afl_player_tracking_and_crowd_monitoring\player_service" `
    -NoNewWindow


# --------------------------------------------------
# Crowd Monitoring Service - Port 8002
# --------------------------------------------------

Write-Host "Starting Crowd Service (port 8002)..."

Start-Process `
    -FilePath "python" `
    -ArgumentList "-m uvicorn shared.services.main:app --host 0.0.0.0 --port 8002" `
    -WorkingDirectory "$root\afl_player_tracking_and_crowd_monitoring\Crowd_Monitoring" `
    -NoNewWindow


# --------------------------------------------------
# Backend Gateway - Port 8000
# --------------------------------------------------

Write-Host "Starting Backend Gateway (port 8000)..."

Start-Process `
    -FilePath "python" `
    -ArgumentList "-m uvicorn app.main:app --host 0.0.0.0 --port 8000" `
    -WorkingDirectory "$root\Backend" `
    -NoNewWindow


# --------------------------------------------------
# Wait for services
# --------------------------------------------------

Write-Host "`nWaiting for services to start..."
Start-Sleep -Seconds 10


# --------------------------------------------------
# Health Checks
# --------------------------------------------------

Write-Host "`nChecking services:"

try {
    $p = Invoke-RestMethod http://localhost:8080/
    Write-Host "  Player Service   (8080): OK - $($p.service)"
}
catch {
    Write-Host "  Player Service   (8080): FAILED"
}

try {
    Invoke-RestMethod http://localhost:8002/openapi.json | Out-Null
    Write-Host "  Crowd Service    (8002): OK"
}
catch {
    Write-Host "  Crowd Service    (8002): FAILED"
}

try {
    $b = Invoke-RestMethod http://localhost:8000/health
    Write-Host "  Backend Gateway  (8000): OK - $($b.gateway)"
}
catch {
    Write-Host "  Backend Gateway  (8000): FAILED"
}


# --------------------------------------------------
# URLs
# --------------------------------------------------

Write-Host "`n========================================"
Write-Host " Service URLs"
Write-Host "========================================"

Write-Host "Backend Swagger : http://localhost:8000/docs"
Write-Host "Crowd Swagger   : http://localhost:8002/docs"
Write-Host "Player Service  : http://localhost:8080"

Write-Host "`nServices startup complete."