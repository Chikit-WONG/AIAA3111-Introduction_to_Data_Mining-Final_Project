"""Build and package the current print poster from the saved data."""
from pathlib import Path
import hashlib
import json
import runpy
import shutil
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'poster'
BUILD = SOURCE / 'build'
ARTIFACTS = ROOT / 'artifacts'
VERSION = 'V03.2'


def main():
    ARTIFACTS.mkdir(exist_ok=True)
    sys.path.insert(0, str(SOURCE))
    runpy.run_path(str(SOURCE / 'build_poster.py'), run_name='__main__')
    validation = json.loads((BUILD / 'qa/validation.json').read_text(encoding='utf-8'))
    if validation['width_warnings'] or validation['text_outside_page'] or validation['text_overlaps']:
        raise RuntimeError('Poster layout checks failed; inspect poster/build/qa/validation.json')
    for name, target in [('poster_800x1000mm.pdf', 'Poster.pdf'),
                         ('poster_editable.svg', 'Poster.svg'),
                         ('poster_preview.png', 'Poster_preview.png')]:
        shutil.copy2(BUILD / name, ARTIFACTS / target)

    source_names = ['build_poster.py', 'scene_engine.py', 'poster_data.json',
                    'requirements-render.txt', 'README.md', '.gitignore', '海报讲解稿_中文_参考.md']
    files = [SOURCE / name for name in source_names] + [Path(__file__).resolve()] + [
        ARTIFACTS / name for name in ['Poster.pdf', 'Poster.svg', 'Poster_preview.png']]
    records = [{'path': p.relative_to(ROOT).as_posix(),
                'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]
    archive = ARTIFACTS / 'Poster_source.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
        for p in files:
            z.write(p, p.relative_to(ROOT))
        z.writestr('README.md', f'# Poster source package - {VERSION}\n\n'
                   'Print size: 800 x 1000 mm portrait. See poster/README.md for fonts and dependencies.\n\n'
                   'Rebuild from this directory:\n\n'
                   '```powershell\npython -m pip install -r poster/requirements-render.txt\n'
                   'python scripts/build_poster.py\n```\n\n'
                   'Only the current version is included. No external image assets or paid API calls are needed.\n')
        z.writestr('source_manifest.json', json.dumps({'version': VERSION, 'files': records,
                     'external_image_assets': []}, ensure_ascii=False, indent=2))
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
    print(json.dumps({'archive': str(archive), 'archive_bytes': archive.stat().st_size,
                      'packaged_files': [v['path'] for v in records]}, ensure_ascii=True, indent=2))


if __name__ == '__main__':
    main()
