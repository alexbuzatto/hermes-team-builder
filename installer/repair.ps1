<#
.SYNOPSIS
    HERMES TEAM BUILDER - Script de Reparo e Atualização de Personas (Windows).
.DESCRIPTION
    Reinstala os arquivos SOUL.md e reaplica as descrições semânticas de delegação
    sem apagar histórico de conversas, memórias ou credenciais dos perfis.
#>
$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "      HERMES TEAM BUILDER - REPARO E ATUALIZAÇÃO          " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$PythonExe = Get-Command python, py -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source -First 1
if (-not $PythonExe) {
    Write-Error "Python 3 não foi encontrado."
    exit 1
}

$PyScript = @"
import sys
from pathlib import Path
sys.path.insert(0, r'$ProjectRoot')
from core.profile_manager import ProfileManager
from core.delegation_manager import DelegationManager

pm = ProfileManager(Path(r'$ProjectRoot'))
results = pm.sync_all_agents(dry_run=False)
for r in results:
    print(f" -> Atualizado: {r['id'].upper()} ({r['profile']})")

dm = DelegationManager(Path(r'$ProjectRoot'))
dm.verify_descriptions()
print('\n[+] Descrições e SOUL.md restaurados com sucesso!')
"@

$TempRunner = Join-Path $env:TEMP "hermes_team_repair_runner.py"
Set-Content -Path $TempRunner -Value $PyScript -Encoding UTF8
& $PythonExe $TempRunner
Remove-Item $TempRunner -Force -ErrorAction SilentlyContinue

& $PythonExe "$ProjectRoot\core\validator.py"
