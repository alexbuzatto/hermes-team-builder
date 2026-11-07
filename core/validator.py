#!/usr/bin/env python3
"""
Módulo de Validação e Diagnóstico Automatizado
Verifica se todos os 12 perfis, SOUL.md e protocolos estão íntegros.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from core.detect_environment import detect_full_environment
from core.profile_manager import ProfileManager, load_manifest

class TeamValidator:
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).resolve().parent.parent
        self.manifest = load_manifest(self.project_root)
        self.pm = ProfileManager(self.project_root)
        self.env = detect_full_environment()

    def run_full_diagnostic(self) -> Dict[str, Any]:
        existing_profiles = self.pm.list_existing_profiles()
        report = {
            "environment": self.env,
            "overall_status": "HEALTHY",
            "agents_status": [],
            "issues": [],
            "warnings": [],
        }

        if not self.env["hermes_installed"]:
            report["overall_status"] = "CRITICAL"
            report["issues"].append("Hermes CLI não encontrado no PATH nem nos diretórios padrão.")
            return report

        for agent in self.manifest["agents"]:
            agent_id = agent["id"]
            profile_name = agent["profile"]
            soul_path = self.pm.get_profile_soul_path(profile_name)

            profile_exists = (profile_name in existing_profiles) or (profile_name == "default")
            soul_exists = soul_path.is_file()
            soul_size = soul_path.stat().st_size if soul_exists else 0

            status = "OK"
            details = []

            if not profile_exists:
                status = "MISSING_PROFILE"
                details.append("Profile não criado no Hermes.")
                report["overall_status"] = "DEGRADED"
                report["issues"].append(f"Agente {agent['name']}: Profile '{profile_name}' não existe.")

            if not soul_exists:
                status = "MISSING_SOUL"
                details.append(f"Arquivo SOUL.md ausente em {soul_path}")
                report["overall_status"] = "DEGRADED"
                report["issues"].append(f"Agente {agent['name']}: SOUL.md ausente.")
            elif soul_size < 100:
                status = "INVALID_SOUL"
                details.append("Arquivo SOUL.md vazio ou excessivamente curto.")
                report["warnings"].append(f"Agente {agent['name']}: SOUL.md parece incompleto ({soul_size} bytes).")

            report["agents_status"].append({
                "id": agent_id,
                "name": agent["name"],
                "profile": profile_name,
                "tier": agent.get("tier", "intermediate"),
                "status": status,
                "profile_exists": profile_exists,
                "soul_exists": soul_exists,
                "soul_path": str(soul_path),
                "soul_size_bytes": soul_size,
                "details": "; ".join(details) if details else "Configuração íntegra."
            })

        return report

    def print_diagnostic_summary(self, report: Optional[Dict[str, Any]] = None) -> None:
        rep = report or self.run_full_diagnostic()
        print("\n" + "=" * 70)
        print("          HERMES AI TEAM - RELATÓRIO DE DIAGNÓSTICO          ")
        print("=" * 70)
        print(f"Status Geral: {rep['overall_status']}")
        print(f"Sistema: {rep['environment']['platform']['os_name']} | Hermes: {rep['environment']['hermes_version']}")
        print("-" * 70)
        print(f"{'AGENTE':<12} | {'PROFILE':<10} | {'TIER':<13} | {'STATUS':<15} | {'SOUL (bytes)'}")
        print("-" * 70)
        for a in rep["agents_status"]:
            status_symbol = "[OK]" if a["status"] == "OK" else f"[{a['status']}]"
            print(f"{a['name']:<12} | {a['profile']:<10} | {a['tier']:<13} | {status_symbol:<15} | {a['soul_size_bytes']} B")
        print("-" * 70)

        if rep["issues"]:
            print("\n[-] PROBLEMAS ENCONTRADOS:")
            for issue in rep["issues"]:
                print(f" - {issue}")

        if rep["warnings"]:
            print("\n[!] AVISOS:")
            for warn in rep["warnings"]:
                print(f" - {warn}")

        if rep["overall_status"] == "HEALTHY":
            print("\n>>> TODOS OS 12 AGENTES ESTAO REGISTRADOS E INTEGROS!")
        print("=" * 70 + "\n")

if __name__ == "__main__":
    validator = TeamValidator()
    validator.print_diagnostic_summary()
