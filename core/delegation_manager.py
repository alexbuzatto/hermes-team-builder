#!/usr/bin/env python3
"""
Módulo de Configuração de Roteamento e Delegação de Tarefas
Configura o fluxo entre HERMES e os 11 especialistas.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

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

    def verify_descriptions(self) -> Dict[str, bool]:
        """
        Verifica e garante que cada profile especialista possui descrição registrada
        para permitir que o orquestrador/kanban roteie tarefas com precisão semântica.
        """
        results = {}
        if not self.hermes_bin:
            return results

        for agent in self.manifest["agents"]:
            profile = agent["profile"]
            if profile == "default":
                continue
            desc = agent["description"]
            try:
                cmd = [self.hermes_bin, "profile", "describe", profile, desc]
                subprocess.run(cmd, capture_output=True, text=True, check=True)
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
    dm = DelegationManager()
    print("=== DELEGATION MANAGER ===")
    print(f"Total de especialistas gerenciados: {len(dm.manifest['agents']) - 1}")
    print("Roteamento preparado para delegação via profile descriptions e kanban.")
