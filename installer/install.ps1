<#
.SYNOPSIS
    HERMES TEAM BUILDER - Instalador Automatizado para Windows PowerShell.
.DESCRIPTION
    Cria e configura os 12 perfis especializados para o Nous Research Hermes Agent,
    instalando os arquivos SOUL.md, descrições semânticas e protocolos operacionais.
.PARAMETER DryRun
    Apenas simula a instalação sem criar perfis ou gravar arquivos.
.PARAMETER SkipSoul
    Apenas cria os perfis sem sobrescrever os arquivos SOUL.md existentes.
#>
[CmdletBinding()]
param(
    [switch]$DryRun,
    [switch]$SkipSoul
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "         HERMES TEAM BUILDER - INSTALADOR WINDOWS         " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Localizar Python
$PythonExe = Get-Command python, py -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source -First 1
if (-not $PythonExe) {
    Write-Error "Python 3 não foi encontrado no PATH. Por favor instale o Python 3.8+."
    exit 1
}
Write-Host "[+] Python detectado: $PythonExe" -ForegroundColor Green

# 2. Executar Detecção de Ambiente
Write-Host "[+] Analisando ambiente e instalação do Hermes..." -ForegroundColor Yellow
& $PythonExe "$ProjectRoot\core\detect_environment.py"

# 3. Executar Sincronização de Perfis e SOUL.md
Write-Host "`n[+] Instalando os 12 perfis especializados e personas SOUL.md..." -ForegroundColor Yellow

$PyScript = @"
import sys
from pathlib import Path
sys.path.insert(0, r'$ProjectRoot')
from core.profile_manager import ProfileManager

pm = ProfileManager(Path(r'$ProjectRoot'))
results = pm.sync_all_agents(dry_run=$($DryRun.IsPresent))
for r in results:
    status = '[CRIADO]' if r['created'] else '[EXISTENTE]'
    soul = '[SOUL OK]' if r['soul_installed'] else '[SOUL PENDENTE]'
    print(f" -> {r['id'].upper():<10} Profile: {r['profile']:<10} {status} {soul}")

print('\n[+] Perfis e personas sincronizados com sucesso!')
"@

$TempRunner = Join-Path $env:TEMP "hermes_team_install_runner.py"
Set-Content -Path $TempRunner -Value $PyScript -Encoding UTF8
& $PythonExe $TempRunner
Remove-Item $TempRunner -Force -ErrorAction SilentlyContinue

# 4. Diagnóstico Final
Write-Host "`n[+] Executando auditoria final de instalação..." -ForegroundColor Yellow
& $PythonExe "$ProjectRoot\core\validator.py"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Instalação concluída com sucesso!                        " -ForegroundColor Green
Write-Host " Você já pode conversar com o HERMES pelo profile default:" -ForegroundColor White
Write-Host "   hermes chat                                            " -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan
