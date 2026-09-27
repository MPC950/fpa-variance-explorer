"""Build the standalone GitHub Pages report locally; does not publish anything."""
from pathlib import Path
import shutil
import subprocess
import sys


def main():
    root = Path(__file__).resolve().parent.parent
    subprocess.run([sys.executable, str(root / "app" / "analyze.py")],
                   cwd=root / "app", check=True)
    site = root / "_site"
    site.mkdir(exist_ok=True)
    shutil.copyfile(root / "app" / "report" / "variance_report.html", site / "index.html")
    (site / ".nojekyll").write_text("", encoding="utf-8")
    print(f"Pages build: {site / 'index.html'}")


if __name__ == "__main__":
    main()
