# GENESIS_POWERSHELL_SESSION_20250726_1633.ps1
# GENESIS PowerShell Session - Admin Environment Setup
# Created: July 26, 2025 - 16:33 Pacific
# Purpose: Complete admin environment for Claude domain control

# Ensure we're in INDEX-PROJECT
Set-Location "C:\INDEX-PROJECT"

# Clear screen for clean start
Clear-Host

# Welcome message
Write-Host "🌟 GENESIS ADMIN SESSION ACTIVE 🌟" -ForegroundColor Green
Write-Host "📁 Directory: $(Get-Location)" -ForegroundColor Cyan
Write-Host "🎯 Claude has full domain control" -ForegroundColor Yellow
Write-Host "♿ Accessibility mode: Copy-button workflows active" -ForegroundColor Magenta
Write-Host ""

# Show current directory contents
Write-Host "📋 INDEX-PROJECT Contents:" -ForegroundColor White
Get-ChildItem | Format-Table Name, Length, LastWriteTime -AutoSize

Write-Host ""
Write-Host "🚀 Ready for Claude commands!" -ForegroundColor Green
Write-Host "💬 Report results with snips and comments" -ForegroundColor Yellow
Write-Host ""

# Set execution policy for session
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force

# Show admin status
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if ($isAdmin) {
    Write-Host "✅ ADMIN PRIVILEGES CONFIRMED" -ForegroundColor Green
} else {
    Write-Host "⚠️  Admin privileges not detected" -ForegroundColor Red
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════"
Write-Host "GENESIS SESSION READY - CLAUDE DOMAIN CONTROL ACTIVE"
Write-Host "═══════════════════════════════════════════════════════════════"