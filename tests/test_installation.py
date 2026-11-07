#!/usr/bin/env python3
"""
Testes Automatizados para HERMES TEAM BUILDER
Valida manifesto, integridade das 12 personas SOUL.md e módulos core.
"""

import os
import sys
import unittest
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from core.detect_environment import detect_full_environment
from core.profile_manager import load_manifest, ProfileManager
from core.backup_manager import BackupManager

class TestHermesTeamBuilder(unittest.TestCase):

    def setUp(self):
        self.root = project_root
        self.manifest = load_manifest(self.root)

    def test_manifest_contains_twelve_agents(self):
        agents = self.manifest.get("agents", [])
        self.assertEqual(len(agents), 12, "O manifesto deve conter exatamente 12 agentes.")

    def test_all_soul_files_exist_and_are_valid(self):
        agents = self.manifest.get("agents", [])
        for agent in agents:
            agent_id = agent["id"]
            soul_path = self.root / "agents" / agent_id / "SOUL.md"
            self.assertTrue(soul_path.is_file(), f"SOUL.md do agente '{agent_id}' não encontrado em {soul_path}.")
            
            content = soul_path.read_text(encoding="utf-8").lower()
            self.assertGreater(len(content), 200, f"SOUL.md do agente '{agent_id}' está excessivamente curto.")
            self.assertTrue("personalidade" in content, f"SOUL.md de '{agent_id}' deve conter personalidade.")
            self.assertTrue("miss" in content, f"SOUL.md de '{agent_id}' deve conter missao.")

    def test_tiers_are_properly_mapped(self):
        tiers = self.manifest.get("tiers", {})
        self.assertIn("premium", tiers)
        self.assertIn("intermediate", tiers)
        self.assertIn("economic", tiers)

        all_tier_profiles = set()
        for t, val in tiers.items():
            all_tier_profiles.update(val.get("profiles", []))

        manifest_profiles = set(a["id"] for a in self.manifest["agents"])
        self.assertEqual(manifest_profiles, all_tier_profiles, "Todos os 12 agentes devem pertencer a algum tier.")

    def test_protocols_exist(self):
        protocols = ["AGENTS.md", "delegation.yaml", "quality.yaml", "security.yaml"]
        for p in protocols:
            p_path = self.root / "protocols" / p
            self.assertTrue(p_path.is_file(), f"Protocolo {p} não encontrado.")

    def test_backup_manager(self):
        bm = BackupManager(self.root / "tests" / "temp_backups")
        temp_file = self.root / "tests" / "temp_file.txt"
        temp_file.write_text("conteúdo de teste", encoding="utf-8")

        try:
            backup_dest = bm.backup_file(temp_file, "Teste unitário de backup")
            self.assertIsNotNone(backup_dest)
            self.assertTrue(backup_dest.exists())
            
            backups = bm.list_backups()
            self.assertGreaterEqual(len(backups), 1)
        finally:
            if temp_file.exists():
                temp_file.unlink()
            import shutil
            if (self.root / "tests" / "temp_backups").exists():
                shutil.rmtree(self.root / "tests" / "temp_backups")

if __name__ == "__main__":
    unittest.main()
