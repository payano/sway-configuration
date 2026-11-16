#!/usr/bin/env python3
"""Install the curated payload, with file-level backups and reversible restore."""
import argparse
import datetime
import json
import os
from pathlib import Path
import re
import shutil
import tempfile

ROOT = Path(__file__).resolve().parent

def safe_parent(home, path):
    for parent in [path.parent, *path.parent.parents]:
        if parent == home:
            break
        if parent.is_symlink():
            raise SystemExit(f'Refusing symlinked parent: {parent}')
    if path.is_dir() and not path.is_symlink():
        raise SystemExit(f'Expected file, found directory: {path}')

def deploy(home):
    if not re.fullmatch(r'/[a-zA-Z0-9_./-]+', str(home)):
        raise SystemExit('Unsupported HOME characters')
    entries = {str(p.relative_to(ROOT/'payload')): p.read_text().replace('@HOME@', str(home))
               for p in (ROOT/'payload').rglob('*') if p.is_file()}
    # Waybar prefers config over config.jsonc; back up and remove a stale config.
    conflict = home/'.config/waybar/config'
    if conflict.exists() or conflict.is_symlink():
        entries['.config/waybar/config'] = None
    optional = {
        '.config/sway/local.conf': '# Local overrides: outputs, workspace mapping, input devices.\n',
        '.config/kanshi/profiles/portable-empty.conf': '# Save your first layout from the Waybar display menu.\n',
    }
    for rel, text in optional.items():
        if not (home/rel).exists() and not (home/rel).is_symlink():
            entries[rel] = text
    for rel in entries:
        safe_parent(home, home/rel)
    backup_base=home/'.local/state/sway-portable/backups'
    safe_parent(home, backup_base/'placeholder')
    backup_base.mkdir(parents=True, exist_ok=True)
    backup=Path(tempfile.mkdtemp(prefix=datetime.datetime.now().strftime('%Y%m%d-%H%M%S-'), dir=backup_base))
    manifest={'home': str(home), 'files': {}}
    # Complete all backups before replacing any configuration.
    for rel in entries:
        target=home/rel
        existed=target.exists() or target.is_symlink()
        manifest['files'][rel]=existed
        if existed:
            dest=backup/'files'/rel; dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(target,dest,follow_symlinks=False)
    (backup/'manifest.json').write_text(json.dumps(manifest,indent=2))
    for rel,text in entries.items():
        target=home/rel
        if target.is_symlink(): target.unlink()
        if text is None:
            target.unlink(missing_ok=True)
            continue
        target.parent.mkdir(parents=True,exist_ok=True)
        source=ROOT/'payload'/rel
        mode=source.stat().st_mode & 0o777 if source.exists() else 0o644
        with tempfile.NamedTemporaryFile(mode='w',dir=target.parent,delete=False) as out:
            out.write(text); temp=Path(out.name)
        temp.chmod(mode); os.replace(temp,target)
    print(f'Backup: {backup}')
    print(f'Restore config: python3 "{ROOT / "deploy.py"}" --restore "{backup}"')
    return backup

def restore(home, backup):
    manifest=json.loads((backup/'manifest.json').read_text())
    if manifest['home'] != str(home): raise SystemExit('Backup belongs to a different HOME')
    for rel, existed in manifest['files'].items():
        if Path(rel).is_absolute() or '..' in Path(rel).parts: raise SystemExit('Invalid backup path')
        safe_parent(home,home/rel)
        if existed and not ((backup/'files'/rel).exists() or (backup/'files'/rel).is_symlink()):
            raise SystemExit(f'Missing backup file: {rel}')
    for rel,existed in manifest['files'].items():
        target=home/rel
        target.unlink(missing_ok=True)
        if existed:
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(backup/'files'/rel,target,follow_symlinks=False)
    print('Configuration restored. Packages and system services were not changed.')

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--restore',type=Path)
    args=parser.parse_args(); home=Path.home()
    if args.restore: restore(home,args.restore.resolve())
    else: deploy(home)
