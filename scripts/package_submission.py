"""Assemble the required ZIP without environments, binaries or raw data."""
from pathlib import Path
import argparse
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--report-dir',type=Path,default=ROOT.parent/(ROOT.name+'-Report'))
    args=parser.parse_args()
    report=args.report_dir.resolve()/'Report.pdf'
    if not report.exists():
        raise FileNotFoundError('Build the report PDF before packaging')
    group=json.loads((ROOT/'configs/team.json').read_text())['group_id']
    if not group:
        raise ValueError('A confirmed Canvas group identifier is required')
    destination=ROOT/'dist'
    destination.mkdir(exist_ok=True)
    archive=destination/f'Group_{group}_Project.zip'
    allowed_dirs=['retail_rules','configs','tests','docs','results/tables','results/figures']
    files=[ROOT/name for name in ['README.md','pyproject.toml','requirements-lock.txt','run.py','data/source_manifest.json']]
    files+=sorted((ROOT/'results').glob('*.json'))
    files+=sorted((ROOT/'scripts').glob('*.py'))+sorted((ROOT/'scripts').glob('*.ps1'))
    for name in allowed_dirs:
        files += sorted(p for p in (ROOT/name).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc')
    records=[]
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        z.write(report,'Report.pdf')
        for source in sorted(set(files)):
            rel=source.relative_to(ROOT).as_posix()
            z.write(source,rel)
            records.append({'file':rel,'sha256':hashlib.sha256(source.read_bytes()).hexdigest()})
        records.append({'file':'Report.pdf','sha256':hashlib.sha256(report.read_bytes()).hexdigest()})
        # Include editable report source without generated build caches.
        for name in ['main.tex','references.bib','latexmkrc','README.md']:
            z.write(args.report_dir/name,'report_source/'+name)
        for folder in ['sections','generated','figures']:
            for source in sorted((args.report_dir/folder).rglob('*')):
                if source.is_file():
                    z.write(source,'report_source/'+source.relative_to(args.report_dir).as_posix())
        z.writestr('submission_manifest.json',json.dumps({'group':group,'files':records,'data_policy':'Full public data reproducible from official download command and checksum; workbook not embedded','poster_policy':'Poster.pdf is delivered separately'},indent=2))
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert 'Report.pdf' in z.namelist()
        assert 'Poster.pdf' not in z.namelist()
        assert not any('.venv/' in n or 'data/raw/' in n or 'tools/bin/' in n for n in z.namelist())
    print(f'{archive} ({archive.stat().st_size/1024/1024:.2f} MiB)')


if __name__=='__main__':
    main()
