#!/usr/bin/env python3
"""
Módulo de Gerenciamento de Backups e Restauração Segura
Cria cópias com timestamp antes de modificar perfis e configurações.
"""

import json
import shutil
import time
from pathlib import Path
from typing import Dict, List, Optional

class BackupManager:
    def __init__(self, backup_dir: Optional[Path] = None):
        if backup_dir is None:
            project_root = Path(__file__).resolve().parent.parent
            self.backup_dir = project_root / "backups"
        else:
            self.backup_dir = Path(backup_dir)

        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_file = self.backup_dir / "backup_manifest.json"
        self._ensure_manifest()

    def _ensure_manifest(self) -> None:
        if not self.manifest_file.exists():
            with open(self.manifest_file, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2)

    def _read_manifest(self) -> List[Dict]:
        try:
            with open(self.manifest_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _write_manifest(self, entries: List[Dict]) -> None:
        with open(self.manifest_file, "w", encoding="utf-8") as f:
            json.dump(entries, f, indent=2, ensure_ascii=False)

    def backup_file(self, target_file: Path, description: str = "") -> Optional[Path]:
        target = Path(target_file)
        if not target.exists():
            return None

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        safe_name = f"{target.stem}_{timestamp}{target.suffix}"
        dest = self.backup_dir / safe_name

        shutil.copy2(target, dest)

        entry = {
            "original_path": str(target.resolve()),
            "backup_path": str(dest.resolve()),
            "timestamp": timestamp,
            "description": description,
            "size_bytes": dest.stat().st_size,
        }

        manifest = self._read_manifest()
        manifest.append(entry)
        self._write_manifest(manifest)

        return dest

    def list_backups(self) -> List[Dict]:
        return self._read_manifest()

    def restore_latest_for(self, target_file: Path) -> bool:
        target_str = str(Path(target_file).resolve())
        manifest = self._read_manifest()
        matches = [e for e in manifest if e["original_path"] == target_str]
        if not matches:
            return False

        latest = matches[-1]
        backup_path = Path(latest["backup_path"])
        if not backup_path.exists():
            return False

        shutil.copy2(backup_path, target_file)
        return True

if __name__ == "__main__":
    bm = BackupManager()
    print(f"Diretório de backups configurado em: {bm.backup_dir}")
    print(f"Backups existentes: {len(bm.list_backups())}")
