"""Assemble the required ZIP without environments, binaries or raw data."""
from pathlib import Path
import argparse
import hashlib
import json
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--report-dir',type=Path,default=ROOT.parent/(ROOT.name+'-Report'))
    args=parser.parse_args()
    report_dir = args.report_dir.resolve()
    report = report_dir / 'Report.pdf'
    for source in (report, report_dir / 'Report.docx'):
        if not source.is_file():
            raise FileNotFoundError(source)
    group=json.loads((ROOT/'configs/team.json').read_text())['group_id']
    if not group:
        raise ValueError('A confirmed Canvas group identifier is required')
    destination=ROOT/'dist'
    destination.mkdir(exist_ok=True)
    archive=destination/f'Group_{group}_Project.zip'
    allowed_dirs=['retail_rules','configs','tests','docs','results/tables','results/figures','poster']
    files=[ROOT/name for name in ['README.md','pyproject.toml','requirements-lock.txt','run.py','data/source_manifest.json']]
    files+=sorted((ROOT/'results').glob('*.json'))
    files+=sorted((ROOT/'scripts').glob('*.py'))+sorted((ROOT/'scripts').glob('*.ps1'))
    for name in allowed_dirs:
        files += sorted(p for p in (ROOT/name).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc' and not (name=='poster' and 'build' in p.relative_to(ROOT/name).parts))
    contents = {p.relative_to(ROOT).as_posix(): p for p in files}
    contents['Report.pdf'] = report
    for name in ['Report.docx', 'main.tex', 'references.bib', 'latexmkrc', 'README.md']:
        contents['report_source/' + name] = report_dir / name
    for folder in ['sections', 'generated', 'figures', 'evidence']:
        for source in (report_dir / folder).rglob('*'):
            if source.is_file():
                contents['report_source/' + source.relative_to(report_dir).as_posix()] = source
    # Publish only a complete, verified archive, including on repeat builds.
    with tempfile.TemporaryDirectory(dir=destination) as staging:
        candidate = Path(staging) / archive.name
        records = []
        with zipfile.ZipFile(candidate, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
            for name, source in sorted(contents.items()):
                data = source.read_bytes()
                z.writestr(name, data)
                records.append({'file': name, 'sha256': hashlib.sha256(data).hexdigest()})
            z.writestr('submission_manifest.json', json.dumps({
                'group': group, 'files': records,
                'data_policy': 'Download the public workbook with python run.py download. See data/source_manifest.json for the checksum.',
                'poster_policy': 'Poster.pdf is optional for Canvas and is omitted from this archive.',
            }, indent=2))
        with zipfile.ZipFile(candidate) as z:
            assert z.testzip() is None
            assert {'Report.pdf', 'report_source/Report.docx', 'README.md', 'run.py', 'data/source_manifest.json'} <= set(z.namelist())
            assert 'Poster.pdf' not in z.namelist()
            assert not any('.venv/' in n or 'data/raw/' in n or 'tools/bin/' in n for n in z.namelist())
        candidate.replace(archive)
    print(f'{archive} ({archive.stat().st_size/1024/1024:.2f} MiB)')


if __name__=='__main__':
    main()
