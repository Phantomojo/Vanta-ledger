# PowerShell script to start VantaLedger backend and frontend

# Function to stop child processes on exit
function Cleanup {
    Write-Host "Stopping VantaLedger backend and frontend..."
    if ($backendProcess -and !$backendProcess.HasExited) {
        $backendProcess.Kill()
        $backendProcess.WaitForExit()
    }
    if ($frontendProcess -and !$frontendProcess.HasExited) {
        $frontendProcess.Kill()
        $frontendProcess.WaitForExit()
    }
    Write-Host "Stopped."
    exit
}

# Register Ctrl+C handler
$null = Register-EngineEvent PowerShell.Exiting -Action { Cleanup }

# Check if src directory exists
if (-not (Test-Path -Path "src" -PathType Container)) {
    Write-Host "Directory 'src' not found. Are you in the project root?"
    exit 1
}

Write-Host "Starting VantaLedger backend..."
$envVars = @{ "PYTHONPATH" = "src" }
$backendProcess = Start-Process -FilePath "python" -ArgumentList "-m", "uvicorn", "vanta_ledger.main:app", "--host", "0.0.0.0", "--port", "8500", "--reload" -NoNewWindow -PassThru -Environment $envVars

Start-Sleep -Seconds 3

if (-not $backendProcess.HasExited) {
    Write-Host "Backend started successfully with PID $($backendProcess.Id)"
} else {
    Write-Host "Backend failed to start"
    exit 1
}

Write-Host "Starting frontend server on port 8001..."
$frontendProcess = Start-Process -FilePath "python" -ArgumentList "-m", "http.server", "8001", "--directory", "../frontend" -NoNewWindow -PassThru

Start-Sleep -Seconds 3

if (-not $frontendProcess.HasExited) {
    Write-Host "Frontend server started successfully with PID $($frontendProcess.Id)"
} else {
    Write-Host "Frontend server failed to start"
    if (-not $backendProcess.HasExited) {
        $backendProcess.Kill()
    }
    exit 1
}

Write-Host "VantaLedger is running."
Write-Host "Backend: http://localhost:8500/"
Write-Host "Frontend: http://localhost:8001/"
Write-Host "Press Ctrl+C to stop."

# Wait for both processes
while (-not ($backendProcess.HasExited -or $frontendProcess.HasExited)) {
    Start-Sleep -Seconds 1
}

Cleanup
