#!/usr/bin/env python3
"""
Módulo de Detecção de Ambiente (Sistema Operacional, Hermes e Caminhos)
Suporta Windows nativo, Linux, WSL2 e macOS.
"""

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, Optional

def get_platform_info() -> Dict[str, Any]:
    system = platform.system().lower()
    is_windows = system == "windows"
    is_linux = system == "linux"
    is_darwin = system == "darwin"
    is_wsl = False

    if is_linux:
        try:
            with open("/proc/version", "r") as f:
                if "microsoft" in f.read().lower():
                    is_wsl = True
        except Exception:
            pass

    return {
        "os_name": platform.system(),
        "release": platform.release(),
        "is_windows": is_windows,
        "is_linux": is_linux,
        "is_darwin": is_darwin,
        "is_wsl": is_wsl,
        "python_version": sys.version.split()[0],
    }

def find_hermes_executable() -> Optional[str]:
    # 1. Checa PATH
    exe = shutil.which("hermes")
    if exe:
        return exe

    # 2. Checa caminhos padrão no Windows
    if platform.system().lower() == "windows":
        local_app_data = os.environ.get("LOCALAPPDATA", "")
        if local_app_data:
            candidate = Path(local_app_data) / "hermes" / "bin" / "hermes.exe"
            if candidate.is_file():
                return str(candidate)

    # 3. Checa caminhos padrão no Linux/macOS
    home = Path.home()
    candidates = [
        home / ".hermes" / "bin" / "hermes",
        home / ".local" / "bin" / "hermes",
        Path("/usr/local/bin/hermes"),
    ]
    for cand in candidates:
        if cand.is_file():
            return str(cand)

    return None

def get_hermes_home() -> Path:
    """
    Retorna o diretório base do Hermes para o profile default.
    No Windows: %LOCALAPPDATA%\\hermes (se existir) ou ~/.hermes
    No Linux/macOS: ~/.hermes
    """
    custom_home = os.environ.get("HERMES_HOME")
    if custom_home:
        return Path(custom_home).resolve()

    if platform.system().lower() == "windows":
        local_app_data = os.environ.get("LOCALAPPDATA")
        if local_app_data:
            path = Path(local_app_data) / "hermes"
            if path.exists() or not (Path.home() / ".hermes").exists():
                return path

    return Path.home() / ".hermes"

def get_hermes_version(hermes_bin: Optional[str] = None) -> Optional[str]:
    bin_path = hermes_bin or find_hermes_executable()
    if not bin_path:
        return None
    try:
        res = subprocess.run([bin_path, "--version"], capture_output=True, text=True, check=True)
        return res.stdout.strip()
    except Exception:
        return None

def detect_full_environment() -> Dict[str, Any]:
    plat = get_platform_info()
    hermes_bin = find_hermes_executable()
    hermes_version = get_hermes_version(hermes_bin)
    hermes_home = get_hermes_home()
    profiles_dir = hermes_home / "profiles"

    return {
        "platform": plat,
        "hermes_bin": hermes_bin,
        "hermes_version": hermes_version,
        "hermes_installed": hermes_bin is not None,
        "hermes_home": str(hermes_home),
        "profiles_dir": str(profiles_dir),
    }

if __name__ == "__main__":
    env = detect_full_environment()
    print("=== HERMES TEAM BUILDER - AMBIENTE DETECTADO ===")
    print(f"Sistema Operacional: {env['platform']['os_name']} ({'WSL2' if env['platform']['is_wsl'] else 'Nativo'})")
    print(f"Python: {env['platform']['python_version']}")
    print(f"Hermes Executável: {env['hermes_bin'] or 'NÃO ENCONTRADO'}")
    print(f"Hermes Versão: {env['hermes_version'] or 'Desconhecida'}")
    print(f"Hermes Home: {env['hermes_home']}")
    print(f"Diretório de Profiles: {env['profiles_dir']}")
