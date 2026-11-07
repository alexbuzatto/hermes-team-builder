#!/usr/bin/env python3
"""
Módulo de Configuração de Roteamento e Delegação de Tarefas
Configura o plugin oficial advanced-delegation e as rotas profile_routes.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from core.detect_environment import detect_full_environment
from core.profile_manager import load_manifest

class DelegationManager:
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).resolve().parent.parent
        self.manifest = load_manifest(self.project_root)
        self.env_info = detect_full_environment()
        self.hermes_bin = self.env_info["hermes_bin"]
        self.hermes_home = Path(self.env_info["hermes_home"])

    def setup_advanced_delegation(self) -> Dict[str, Any]:
        """
        Instala e habilita o plugin oficial advanced-delegation e
        salva as rotas profile_routes para os 11 especialistas.
        """
        status = {
            "plugin_installed": False,
            "plugin_enabled": False,
            "backend_set": False,
            "routes_saved": False,
            "details": ""
        }
        if not self.hermes_bin:
            status["details"] = "Hermes CLI não encontrado."
            return status

        # 1. Instalar plugin se necessário
        try:
            cmd = [self.hermes_bin, "plugins", "install", "advanced-delegation"]
            subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            status["plugin_installed"] = True
        except Exception as e:
            status["details"] += f"Install plugin: {e}. "

        # 2. Habilitar plugin
        try:
            cmd = [self.hermes_bin, "plugins", "enable", "advanced-delegation"]
            subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            status["plugin_enabled"] = True
        except Exception as e:
            status["details"] += f"Enable plugin: {e}. "

        # 3. Configurar backend = profile_routes
        try:
            cmd = [self.hermes_bin, "config", "set", "delegation.backend", "profile_routes"]
            subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            status["backend_set"] = True
        except Exception as e:
            status["details"] += f"Set backend: {e}. "

        # 4. Salvar perfis via store.py do plugin usando python com ruamel se disponível
        profiles = []
        for agent in self.manifest["agents"]:
            if agent["profile"] == "default":
                continue
            profiles.append({
                "name": agent["profile"],
                "description": agent["description"]
            })

        plugin_dir = self.hermes_home / "plugins" / "advanced-delegation"
        agent_dir = self.hermes_home / "hermes-agent"
        store_script = f"""
import sys
for p in [r'{plugin_dir}', r'{agent_dir}']:
    if p not in sys.path:
        sys.path.insert(0, p)
try:
    from store import save_profiles, set_mode
    profiles = {profiles!r}
    set_mode('profile_routes')
    save_profiles(profiles)
    print('ROUTES_SAVED_OK')
except Exception as e:
    print(f'ERROR: {{e}}')
"""
        # Tenta executar com o python do venv ou python do sistema
        venv_candidates = list(self.hermes_home.glob("**/venv/Scripts/python.exe")) + \
                          list(self.hermes_home.glob("**/bin/python"))
        py_exe = str(venv_candidates[0]) if venv_candidates else sys.executable

        try:
            res = subprocess.run([py_exe, "-c", store_script], capture_output=True, text=True, timeout=30)
            if "ROUTES_SAVED_OK" in res.stdout:
                status["routes_saved"] = True
            else:
                status["details"] += f"Routes error: {res.stderr or res.stdout}"
        except Exception as e:
            status["details"] += f"Execute store script: {e}."

        return status

    def verify_descriptions(self) -> Dict[str, bool]:
        """Garante que cada profile especialista possui descrição registrada."""
        results = {}
        if not self.hermes_bin:
            return results

        for agent in self.manifest["agents"]:
            profile = agent["profile"]
            if profile == "default":
                continue
            desc = agent["description"]
            try:
                cmd = [self.hermes_bin, "profile", "describe", profile, "--text", desc]
                subprocess.run(cmd, capture_output=True, text=True, timeout=10, check=True)
                results[profile] = True
            except Exception:
                results[profile] = False

        return results

    def sync_project_protocol(self, target_project_dir: Path) -> bool:
        """Copia o AGENTS.md e templates de tarefa para a raiz de um projeto."""
        target_dir = Path(target_project_dir)
        if not target_dir.exists():
            target_dir.mkdir(parents=True, exist_ok=True)

        source_agents = self.project_root / "protocols" / "AGENTS.md"
        dest_agents = target_dir / "AGENTS.md"

        if source_agents.exists():
            import shutil
            shutil.copy2(source_agents, dest_agents)
            return True
        return False

if __name__ == "__main__":
    from typing import Any
    dm = DelegationManager()
    res = dm.setup_advanced_delegation()
    print("=== DELEGATION SETUP RESULT ===")
    print(res)
