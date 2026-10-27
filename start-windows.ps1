$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
if (-not (Get-Command node -ErrorAction SilentlyContinue)) { throw 'Install Node.js 20+ first.' }
if (-not $env:ALICE_PANEL_TOKEN) { throw 'Set ALICE_PANEL_TOKEN before starting.' }
if (-not $env:ALICE_BIND) { $env:ALICE_BIND = '0.0.0.0' }
node node/server.js
