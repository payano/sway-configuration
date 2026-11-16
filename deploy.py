#!/usr/bin/env python3
"""Link tracked configuration; keep host settings and reversible backups outside Git."""
import argparse
import datetime
import json
import os
from pathlib import Path
import shutil
import tempfile

ROOT = Path(__file__).resolve().parent
CONFIGS = ('sway', 'waybar', 'dunst', 'foot', 'kanshi')
HELPERS = ('start-kanshi', 'save-kanshi-profile', 'float-chromium-notifications')


def exists(path):
    return path.exists() or path.is_symlink()


def check_parent(home, path):
    for parent in [path.parent, *path.parent.parents]:
        if parent == home:
            break
        if parent.is_symlink():
            raise SystemExit(f'Refusing symlinked parent: {parent}')
        if parent.exists() and not parent.is_dir():
            raise SystemExit(f'Expected directory: {parent}')


def links():
    return {**{f'.config/{name}': ROOT/'payload/.config'/name for name in CONFIGS},
            **{f'.local/bin/{name}': ROOT/'payload/.local/bin'/name for name in HELPERS}}


def matches(path, source):
    return path.is_symlink() and path.resolve() == source.resolve()


def prepare_local(home):
    """Preserve local overrides/profiles, including the original workspace mapping."""
    local = home/'.config/sway-local'
    check_parent(home, local/'placeholder')
    local.mkdir(parents=True, exist_ok=True)
    config = local/'config'
    if not exists(config):
        old = home/'.config/sway/local.conf'
        text = old.read_text() if old.is_file() else ''
        original = home/'.config/sway/config'
        if original.is_file():
            text += '\n'.join(line for line in original.read_text().splitlines()
                              if line.strip().startswith('workspace ') and ' output ' in line) + '\n'
        config.write_text('# Machine-local Sway overrides; not versioned.\n' + text)
    profiles = local/'kanshi-profiles'
    check_parent(home, profiles/'placeholder')
    if not exists(profiles):
        old = home/'.config/kanshi/profiles'
        if old.is_dir():
            shutil.copytree(old, profiles, symlinks=True)
        else:
            profiles.mkdir()
        (profiles/'portable-empty.conf').write_text('# Save layouts using the Waybar display menu.\n')


def deploy(home):
    mapping = links()
    pending = {}
    for rel, source in mapping.items():
        target = home/rel
        check_parent(home, target)
        if not source.exists():
            raise SystemExit(f'Missing repo source: {source}')
        if not matches(target, source):
            pending[rel] = source
    backup_base = home/'.local/state/sway-portable/backups'
    check_parent(home, backup_base/'placeholder')
    # Preserve host-specific settings before moving any original directories.
    prepare_local(home)
    if not pending:
        print('All links already point to this repo; nothing to replace.')
        return None
    backup_base.mkdir(parents=True, exist_ok=True)
    backup = Path(tempfile.mkdtemp(prefix=datetime.datetime.now().strftime('%Y%m%d-%H%M%S-'), dir=backup_base))
    manifest = {'version': 2, 'home': str(home), 'links': {
        rel: {'source': str(source), 'existed': exists(home/rel)} for rel, source in pending.items()}}
    (backup/'manifest.json').write_text(json.dumps(manifest, indent=2))
    applied = []
    try:
        for rel, source in pending.items():
            target = home/rel
            saved = backup/'files'/rel
            saved.parent.mkdir(parents=True, exist_ok=True)
            target.parent.mkdir(parents=True, exist_ok=True)
            if exists(target):
                shutil.move(str(target), str(saved))
            applied.append(rel)
            target.symlink_to(source, target_is_directory=source.is_dir())
    except BaseException:
        for rel in reversed(applied):
            target = home/rel
            saved = backup/'files'/rel
            if target.is_symlink(): target.unlink()
            if exists(saved): shutil.move(str(saved), str(target))
        (backup/'rolled-back').touch()
        raise
    print(f'Linked {len(pending)} paths to {ROOT}')
    print(f'Backup: {backup}')
    print(f'Restore: python3 "{ROOT / "deploy.py"}" --restore "{backup}"')
    return backup


def restore(home, backup):
    manifest = json.loads((backup/'manifest.json').read_text())
    if manifest.get('version') != 2:
        raise SystemExit('Legacy copy backup: use deploy.py from Git commit d397e6a to restore it.')
    if manifest['home'] != str(home):
        raise SystemExit('Backup belongs to a different HOME')
    if (backup/'restored').exists() or (backup/'rolled-back').exists():
        raise SystemExit('This backup has already been restored or rolled back.')
    for rel, item in manifest['links'].items():
        if rel not in links(): raise SystemExit(f'Unexpected backup path: {rel}')
        target = home/rel
        check_parent(home, target)
        if exists(target) and (not target.is_symlink() or os.readlink(target) != item['source']):
            raise SystemExit(f'Destination has changed; leaving it untouched: {target}')
        if item['existed'] and not exists(backup/'files'/rel):
            raise SystemExit(f'Missing backup: {rel}')
    for rel, item in manifest['links'].items():
        target = home/rel
        target.unlink(missing_ok=True)
        if item['existed']:
            saved = backup/'files'/rel
            if saved.is_dir() and not saved.is_symlink():
                shutil.copytree(saved, target, symlinks=True)
            else:
                shutil.copy2(saved, target, follow_symlinks=False)
    (backup/'restored').touch()
    print('Original paths restored. Repo, sway-local, packages and services were retained.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--restore', type=Path)
    args = parser.parse_args()
    home = Path.home()
    if os.geteuid() == 0:
        parser.error('Run as your normal user, not root.')
    if os.environ.get('XDG_CONFIG_HOME', str(home/'.config')) != str(home/'.config'):
        parser.error('Custom XDG_CONFIG_HOME is not supported.')
    if args.restore:
        restore(home, args.restore.resolve())
    else:
        deploy(home)
