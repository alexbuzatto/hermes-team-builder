<#
.SYNOPSIS
    HERMES TEAM BUILDER - Desinstalador Seguro (Windows).
.DESCRIPTION
    Remove os 11 perfis de especialistas criados, preservando o perfil default,
    backups e arquivos de projeto.
#>
param(
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Write-Host "==========================================================" -ForegroundColor Red
Write-Host "         HERMES TEAM BUILDER - DESINSTALADOR SEGURO       " -ForegroundColor Red
Write-Host "==========================================================" -ForegroundColor Red

$Specialists = @(
    "athena", "atlas", "tesla", "ada", "linus", 
    "iris", "sherlock", "sentinel", "nova", "scribe", "arbiter"
)

Write-Host "Esta operação removerá os 11 profiles especialistas do Hermes:" -ForegroundColor Yellow
$Specialists | ForEach-Object { Write-Host " - $_" -ForegroundColor Gray }
Write-Host "O profile principal 'default' e seus projetos NÃO serão afetados.`n" -ForegroundColor Green

if (-not $Force) {
    $Confirm = Read-Host "Tem certeza de que deseja continuar? (s/N)"
    if ($Confirm -ne "s" -and $Confirm -ne "S") {
        Write-Host "Operação cancelada pelo usuário." -ForegroundColor Yellow
        exit 0
    }
}

foreach ($spec in $Specialists) {
    Write-Host "Removendo profile '$spec'..." -ForegroundColor Yellow
    hermes profile delete $spec --yes 2>$null
}

Write-Host "`n[+] Especialistas removidos. O profile principal default foi preservado." -ForegroundColor Green
