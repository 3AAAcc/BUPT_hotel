@echo off
chcp 65001 >nul
echo ========================================
echo Setup Firewall for Port 8000
echo ========================================
echo.
echo This will configure Windows Firewall to allow
echo connections on port 8000 for the Hotel AC System.
echo.
echo This only needs to be run ONCE (not every time you start the server).
echo.
echo This operation requires administrator privileges.
echo.

:: Check for administrator privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Requesting administrator privileges...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo Configuring firewall...
powershell -Command "Remove-NetFirewallRule -DisplayName 'Hotel AC System Port 8000' -ErrorAction SilentlyContinue; New-NetFirewallRule -DisplayName 'Hotel AC System Port 8000' -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow -Profile Domain,Private,Public -Description 'Allow Hotel AC Management System on port 8000'; if ($?) { Write-Host 'Success! Firewall rule configured.' -ForegroundColor Green; Write-Host ''; Write-Host 'You can now start the server. This firewall setup only needs to be done once.' -ForegroundColor Cyan } else { Write-Host 'Error: Failed to configure firewall.' -ForegroundColor Red }"

echo.
pause

