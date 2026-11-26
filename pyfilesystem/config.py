from pathlib import Path
import os

APP_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = APP_ROOT / "data"
DATA_FILE = DATA_DIR / "simulation.json"
# Linux worker's ONLY permitted real-operation root.
LINUX_LAB_ROOT = Path.home() / "pyfilesystem_lab" / "lab_test"
DEFAULT_DISK_KB = 100
DEFAULT_BLOCK_KB = 1
