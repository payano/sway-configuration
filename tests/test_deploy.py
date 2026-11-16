import importlib.util
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('deploy', SOURCE/'deploy.py')
deploy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(deploy)


class DeploymentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        base = Path(self.temp.name)
        self.home = base/'home'
        self.home.mkdir()
        self.repo = base/'repo'
        shutil.copytree(SOURCE/'payload', self.repo/'payload')
        self.root = patch.object(deploy, 'ROOT', self.repo)
        self.root.start()
        self.addCleanup(self.root.stop)
        original = self.home/'.config/sway'
        original.mkdir(parents=True)
        (original/'config').write_text('workspace 1 output DP-8 eDP-1\n')
        (original/'local.conf').write_text('# custom local\n')
        profiles = self.home/'.config/kanshi/profiles'
        profiles.mkdir(parents=True)
        (profiles/'laptop.conf').write_text('# laptop profile\n')

    def test_links_edits_idempotence_and_restore(self):
        backup = deploy.deploy(self.home)
        for rel, source in deploy.links().items():
            self.assertTrue((self.home/rel).is_symlink())
            self.assertEqual((self.home/rel).resolve(), source.resolve())
        config = self.home/'.config/dunst/dunstrc'
        config.write_text('# edit through live path\n')
        self.assertEqual((self.repo/'payload/.config/dunst/dunstrc').read_text(), config.read_text())
        self.assertIn('workspace 1 output DP-8', (self.home/'.config/sway-local/config').read_text())
        self.assertIn('# custom local', (self.home/'.config/sway-local/config').read_text())
        self.assertTrue((self.home/'.config/sway-local/kanshi-profiles/laptop.conf').is_file())
        self.assertFalse((self.repo/'payload/.config/kanshi/profiles').exists())
        self.assertIsNone(deploy.deploy(self.home))
        deploy.restore(self.home, backup)
        self.assertFalse((self.home/'.config/sway').is_symlink())
        self.assertEqual((self.home/'.config/sway/config').read_text(), 'workspace 1 output DP-8 eDP-1\n')
        self.assertFalse((self.home/'.config/dunst').exists())
        self.assertEqual((self.repo/'payload/.config/dunst/dunstrc').read_text(), '# edit through live path\n')

    def test_other_symlink_is_preserved(self):
        old = self.home/'old-dunst'; old.mkdir()
        (old/'dunstrc').write_text('old')
        (self.home/'.config/dunst').symlink_to(old)
        backup = deploy.deploy(self.home)
        deploy.restore(self.home, backup)
        self.assertEqual((self.home/'.config/dunst').resolve(), old)
        self.assertEqual((old/'dunstrc').read_text(), 'old')

    def test_refuse_parent_symlink(self):
        elsewhere = self.home/'elsewhere'; elsewhere.mkdir()
        (self.home/'.local').symlink_to(elsewhere)
        with self.assertRaises(SystemExit): deploy.deploy(self.home)
        self.assertFalse((self.home/'.config/sway').is_symlink())

    def test_link_failure_rolls_back(self):
        original = Path.symlink_to
        def fail(path, target, **kwargs):
            if path.name == 'dunst': raise OSError('simulated link failure')
            return original(path, target, **kwargs)
        with patch.object(Path, 'symlink_to', fail):
            with self.assertRaises(OSError): deploy.deploy(self.home)
        self.assertFalse((self.home/'.config/sway').is_symlink())
        self.assertTrue((self.home/'.config/sway/local.conf').is_file())
        self.assertFalse((self.home/'.config/waybar').exists())

    def test_restore_refuses_replaced_directory(self):
        backup = deploy.deploy(self.home)
        target = self.home/'.config/sway'
        target.unlink(); target.mkdir(); (target/'new').touch()
        with self.assertRaises(SystemExit): deploy.restore(self.home, backup)
        self.assertTrue((target/'new').exists())


if __name__ == '__main__': unittest.main()
