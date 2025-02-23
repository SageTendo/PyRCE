import re
from pathlib import Path

HOST = "localhost"
PORT = 6000

IPV4_PATTERN = re.compile(r'^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{1,5})$')

BASE_DIR = Path(__file__).resolve().parent
DOWNLOAD_DIR = BASE_DIR / "Downloads"

if not DOWNLOAD_DIR.exists():
    DOWNLOAD_DIR.mkdir()

# Helpers
KB = 1024
MB = KB ** 2
FILE_CHUNK_SIZE = 5 * MB
