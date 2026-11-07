#!/usr/bin/env python3
"""
Módulo de Gerenciamento de Perfis (Hermes Profiles)
Criação, verificação, instalação de SOUL.md e descrições dos 12 perfis.
Zero dependências externas obrigatórias (usa json como fallback nativo para yaml).
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from core.detect_environment import detect_full_environment
from core.backup_manager import BackupManager

def load_manifest(project_root: Path) -> Dict:
    json_path = project_root / "manifest.json"
    if json_path.exists():
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)

    yaml_path = project_root / "manifest.yaml"
    if yaml_path.exists():
        try:
            import yaml
            with open(yaml_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except ImportError:
            pass

    raise FileNotFoundError("Não foi possível carregar manifest.json ou manifest.yaml.")

class ProfileManager:
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).resolve().parent.parent
        self.manifest = load_manifest(self.project_root)
        self.env_info = detect_full_environment()
        self.hermes_bin = self.env_info["hermes_bin"]
        self.hermes_home = Path(self.env_info["hermes_home"])
        self.profiles_dir = Path(self.env_info["profiles_dir"])
        self.backup_mgr = BackupManager()

    def list_existing_profiles(self) -> List[str]:
        """Consulta os perfis registrados no Hermes CLI."""
        if not self.hermes_bin:
            return []
        try:
            res = subprocess.run(
                [self.hermes_bin, "profile", "list"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=True
            )
            profiles = []
            for line in res.stdout.splitlines():
                line = line.strip()
                if not line or "profile" in line.lower() and "model" in line.lower():
                    continue
                # Procura o primeiro identificador alfanumérico na linha (ex: default, athena)
                match = re.search(r'[a-zA-Z0-9_\-]+', line)
                if match:
                    name = match.group(0).lower()
                    if name not in ("profile", "model", "gateway", "alias", "distribution") and not name.startswith("-"):
                        profiles.append(name)
            return list(dict.fromkeys(profiles))
        except Exception:
            profiles = ["default"]
            if self.profiles_dir.exists():
                for item in self.profiles_dir.iterdir():
                    if item.is_dir():
                        profiles.append(item.name.lower())
            return profiles

    def get_profile_soul_path(self, profile_name: str) -> Path:
        """Determina onde o SOUL.md deve ser colocado para determinado profile."""
        if profile_name == "default":
            return self.hermes_home / "SOUL.md"
        return self.profiles_dir / profile_name / "SOUL.md"

    def create_profile(self, name: str, description: str) -> Tuple[bool, str]:
        """Cria um profile novo via Hermes CLI."""
        if not self.hermes_bin:
            return False, "Binário do Hermes não encontrado."

        try:
            cmd = [self.hermes_bin, "profile", "create", name, "--description", description]
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode == 0:
                return True, "Profile criado com sucesso."
            else:
                return False, (res.stderr or res.stdout).strip()
        except Exception as e:
            return False, str(e)

    def set_profile_description(self, name: str, description: str) -> bool:
        """Atualiza a descrição do profile para o orquestrador/kanban."""
        if not self.hermes_bin or name == "default":
            return False
        try:
            cmd = [self.hermes_bin, "profile", "describe", name, description]
            subprocess.run(cmd, capture_output=True, text=True)
            return True
        except Exception:
            return False

    def install_agent_soul(self, agent_id: str, profile_name: str) -> Dict[str, str]:
        """Instala o arquivo SOUL.md do agente no diretório do profile."""
        source_soul = self.project_root / "agents" / agent_id / "SOUL.md"
        if not source_soul.exists():
            return {"status": "error", "message": f"Fonte não encontrada: {source_soul}"}

        dest_soul = self.get_profile_soul_path(profile_name)
        dest_soul.parent.mkdir(parents=True, exist_ok=True)

        if dest_soul.exists():
            self.backup_mgr.backup_file(
                dest_soul, description=f"Backup antes da instalação de {agent_id}"
            )

        with open(source_soul, "r", encoding="utf-8") as src:
            content = src.read()

        with open(dest_soul, "w", encoding="utf-8") as dst:
            dst.write(content)

        return {"status": "success", "dest": str(dest_soul)}

    def sync_all_agents(self, dry_run: bool = False) -> List[Dict]:
        """Sincroniza todos os 12 agentes do manifesto."""
        results = []
        existing = self.list_existing_profiles()

        for agent in self.manifest["agents"]:
            agent_id = agent["id"]
            profile_name = agent["profile"]
            desc = agent["description"]

            res = {
                "id": agent_id,
                "profile": profile_name,
                "created": False,
                "soul_installed": False,
                "details": ""
            }

            if dry_run:
                res["details"] = "Modo simulação (dry-run)"
                results.append(res)
                continue

            # 1. Criação do Profile se não for default e não existir
            if profile_name != "default" and profile_name not in existing:
                success, msg = self.create_profile(profile_name, desc)
                res["created"] = success
                res["details"] += f"Criação: {msg}. "
            else:
                res["details"] += "Profile já existente. "
                if profile_name != "default":
                    self.set_profile_description(profile_name, desc)

            # 2. Instalação do SOUL.md
            soul_res = self.install_agent_soul(agent_id, profile_name)
            res["soul_installed"] = soul_res["status"] == "success"
            res["details"] += f"SOUL: {soul_res['status']}."

            results.append(res)

        return results

if __name__ == "__main__":
    pm = ProfileManager()
    print("=== PROFILES ATUAIS NO HERMES ===")
    print(pm.list_existing_profiles())
    print("\nExecutando verificação de perfis do manifesto...")
    status = pm.sync_all_agents(dry_run=True)
    for s in status:
        print(f"[{s['id'].upper()}] Profile: {s['profile']} -> {s['details']}")
