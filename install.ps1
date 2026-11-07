<#
.SYNOPSIS
    HERMES TEAM BUILDER - Ponto de Entrada de Instalação (Windows)
#>
$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
& "$ScriptDir\installer\install.ps1" @args
