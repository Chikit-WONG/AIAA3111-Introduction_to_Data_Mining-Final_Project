"""Download a checksum-verified, portable Tectonic for optional Windows QA."""
from pathlib import Path
import hashlib
import shutil
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
URL = "https://github.com/tectonic-typesetting/tectonic/releases/download/tectonic%400.17.0/tectonic-0.17.0-x86_64-pc-windows-msvc.zip"
SHA256 = "f61ce51f0b0ade1015b7de7ef368541c5424e9756ecbd0d7af97d6d48030845f"


def main():
    dest = ROOT / "tools/bin"
    dest.mkdir(parents=True, exist_ok=True)
    archive = dest / "tectonic.zip"
    if not archive.exists():
        req = urllib.request.Request(URL, headers={"User-Agent": "AIAA3111 local report build"})
        with urllib.request.urlopen(req, timeout=120) as src, archive.open("wb") as dst:
            shutil.copyfileobj(src, dst)
    if hashlib.sha256(archive.read_bytes()).hexdigest() != SHA256:
        raise ValueError("Tectonic release checksum mismatch")
    with zipfile.ZipFile(archive) as z:
        exe = [name for name in z.namelist() if Path(name).name == "tectonic.exe"]
        if len(exe) != 1:
            raise ValueError("Expected one Tectonic executable")
        with z.open(exe[0]) as src, (dest / "tectonic.exe").open("wb") as dst:
            shutil.copyfileobj(src, dst)
    print(dest / "tectonic.exe")


if __name__ == "__main__":
    main()
