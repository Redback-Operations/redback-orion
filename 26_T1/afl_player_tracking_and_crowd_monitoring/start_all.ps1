$root = $PSScriptRoot

Write-Host "Starting Player Service (port 8080)..."
Start-Process -FilePath "python" -ArgumentList "-m uvicorn main:app --host 0.0.0.0 --port 8080" -WorkingDirectory "$root\player_service" -NoNewWindow

Write-Host "Starting Crowd Service (port 8002)..."
Start-Process -FilePath "python" -ArgumentList "-m uvicorn shared.services.main:app --host 0.0.0.0 --port 8002" -WorkingDirectory "$root\Crowd_Monitoring\2026_T1" -NoNewWindow

Write-Host "Starting Backend Gateway (port 8000)..."
Start-Process -FilePath "python" -ArgumentList "-m uvicorn app.main:app --host 0.0.0.0 --port 8000" -WorkingDirectory "$root\backend" -NoNewWindow

Write-Host "Waiting for services to start..."
Start-Sleep -Seconds 10

Write-Host "`nChecking services:"
try { $p = Invoke-RestMethod http://localhost:8080/; Write-Host "  Player Service (8080): OK - $($p.service)" } catch { Write-Host "  Player Service (8080): FAILED" }
try { Invoke-RestMethod http://localhost:8002/openapi.json | Out-Null; Write-Host "  Crowd Service  (8002): OK" } catch { Write-Host "  Crowd Service  (8002): FAILED" }
try { $b = Invoke-RestMethod http://localhost:8000/health; Write-Host "  Backend Gateway(8000): OK - $($b.gateway)" } catch { Write-Host "  Backend Gateway(8000): FAILED" }

Write-Host "`nAll services started. Swagger UI: http://localhost:8000/docs"
