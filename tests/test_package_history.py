import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PackageHistoryTests(unittest.TestCase):
    def run_install(self, home, distro, fail=0):
        script = r'''
source ./package-history.sh
package_snapshot() {
  if [[ -e "$HOME/changed" ]]; then
    printf 'base\t2\ndependency\t1\nwaybar\t1\n'
  else
    printf 'base\t1\nremoved-package\t1\n'
  fi
}
package_explicit() {
  printf 'base\n'
  if [[ -e "$HOME/changed" ]]; then printf 'waybar\n'; fi
}
sudo() {
  printf '%s\n' "$*" >> "$HOME/commands"
  if [[ "$*" = 'apt-get update' ]]; then return 0; fi
  touch "$HOME/changed"
  return "$FAIL"
}
install_packages_logged "$DISTRO" base waybar
'''
        return subprocess.run(['bash', '-c', script], cwd=ROOT, capture_output=True, text=True,
                              env={**os.environ, 'HOME': str(home), 'DISTRO': distro, 'FAIL': str(fail)})

    def test_success_failure_and_repeat(self):
        for distro in ('debian', 'arch'):
            for failure in (0, 42):
                with self.subTest(distro=distro, failure=failure), tempfile.TemporaryDirectory() as tmp:
                    home = Path(tmp)
                    result = self.run_install(home, distro, failure)
                    self.assertEqual(result.returncode, failure, result.stderr)
                    history = next((home/'.local/state/sway-portable/packages').iterdir())
                    self.assertEqual((history/'added.txt').read_text(), 'dependency\nwaybar\n')
                    self.assertEqual((history/'added-requested.txt').read_text(), 'waybar\n')
                    self.assertEqual((history/'removed.txt').read_text(), 'removed-package\n')
                    self.assertEqual((history/'version-changes.tsv').read_text(), 'base\t1\t2\n')
                    self.assertEqual((history/'newly-explicit.txt').read_text(), 'waybar\n')
                    self.assertEqual((history/'package-exit-code').read_text(), f'{failure}\n')
                    expected = 'apt-get update\napt-get install base waybar\n' if distro == 'debian' else 'pacman -Syu --needed base waybar\n'
                    self.assertEqual((home/'commands').read_text(), expected)
                    repeat = self.run_install(home, distro)
                    self.assertEqual(repeat.returncode, 0, repeat.stderr)
                    histories = list((home/'.local/state/sway-portable/packages').iterdir())
                    self.assertEqual(len(histories), 2)
                    latest = next(p for p in histories if p != history)
                    self.assertEqual((latest/'added.txt').read_text(), '')
                    self.assertEqual((history/'added.txt').read_text(), 'dependency\nwaybar\n')

    def test_snapshot_parsers(self):
        script = r'''
set -euo pipefail
source ./package-history.sh
dpkg-query() { printf 'z:amd64\t1\tinstalled\na\t2\tconfig-files\nb\t3\tinstalled\n'; }
pacman() { printf 'z 1\nb 3\n'; }
package_snapshot debian
package_snapshot arch
'''
        result = subprocess.run(['bash', '-c', script], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, 'b\t3\nz:amd64\t1\nb\t3\nz\t1\n')


if __name__ == '__main__': unittest.main()
