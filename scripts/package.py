"""Rebuild the shareable app ZIP from the canonical app folder."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

root = Path(__file__).resolve().parent.parent
app = root / 'app'
destination = root / 'dist' / 'FPA_Variance_Explorer.zip'
destination.parent.mkdir(exist_ok=True)
with ZipFile(destination, 'w', ZIP_DEFLATED) as archive:
    for file in sorted(app.rglob('*')):
        if not file.is_file() or '__pycache__' in file.parts or file.name.endswith('.inspect.ndjson'):
            continue
        archive.write(file, Path('FPA_Variance_Explorer') / file.relative_to(app))
print(destination)
