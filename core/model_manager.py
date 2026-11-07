#!/usr/bin/env python3
"""
Módulo de Configuração de Modelos de Inteligência Artificial por Especialista
Distribui os modelos conforme as categorias (Premium, Intermediário e Econômico).
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

class ModelManager:
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).resolve().parent.parent
        self.manifest = load_manifest(self.project_root)
        self.env_info = detect_full_environment()
        self.hermes_bin = self.env_info["hermes_bin"]

    def set_profile_model(self, profile: str, model_name: str) -> Tuple[bool, str]:
        """Configura o modelo para um profile específico via hermes config set model."""
        if not self.hermes_bin:
            return False, "Binário do Hermes não encontrado."

        try:
            if profile == "default":
                cmd = [self.hermes_bin, "config", "set", "model", model_name]
            else:
                cmd = [self.hermes_bin, "-p", profile, "config", "set", "model", model_name]

            res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
            if res.returncode == 0:
                return True, f"Modelo configurado para {profile}: {model_name}"
            else:
                return False, res.stderr or res.stdout
        except Exception as e:
            return False, str(e)

    def apply_tier_models(self, tier_mapping: Dict[str, str]) -> Dict[str, Dict]:
        """
        Aplica modelos com base nas categorias:
        tier_mapping = {
            "premium": "provedor/modelo_premium",
            "intermediate": "provedor/modelo_intermed",
            "economic": "provedor/modelo_eco"
        }
        """
        results = {}
        for agent in self.manifest["agents"]:
            profile = agent["profile"]
            tier = agent.get("tier", "intermediate")
            chosen_model = tier_mapping.get(tier)

            if chosen_model:
                success, msg = self.set_profile_model(profile, chosen_model)
                results[profile] = {
                    "tier": tier,
                    "model": chosen_model,
                    "success": success,
                    "message": msg
                }
            else:
                results[profile] = {
                    "tier": tier,
                    "model": "mantido (não especificado)",
                    "success": True,
                    "message": "Nenhum modelo informado para este tier."
                }

        return results

if __name__ == "__main__":
    mm = ModelManager()
    print("=== MODEL MANAGER - TIERS DO MANIFESTO ===")
    for tier, info in mm.manifest.get("tiers", {}).items():
        print(f"[{tier.upper()}]: {info['description']} -> {', '.join(info['profiles'])}")
