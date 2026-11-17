Sway-konfiguration för Debian 13 och Arch Linux.

Installera som vanlig användare (kräver sudo och internet):

  git clone git@github.com:payano/sway-configuration.git ~/git/sway-configuration
  cd ~/git/sway-configuration
  ./install.sh

Installerar paket och länkar Sway, Waybar, Dunst, Foot och Kanshi till repot.
Arch uppdateras med pacman -Syu. Starta om och välj Sway vid inloggning.

  ./install.sh --dry-run       Förhandsgranska
  ./install.sh --config-only   Skapa enbart länkar, utan paketinstallation

Ändringar i ~/.config/sway, ~/.config/dunst osv. syns direkt i Git:

  git add payload
  git commit -m "Uppdatera konfiguration"
  git push

På andra datorn: git pull --ff-only och ladda om berörda program.
Behåll repot på disk; länkarna pekar dit.

Datorspecifikt: ~/.config/sway-local/config och kanshi-profiles/.
Skärmlayout sparas via högerklick på Waybars skärmikon.

Backup: ~/.local/state/sway-portable/backups/<id>/
Återställ: python3 deploy.py --restore <backupkatalog>

Tester: python3 -m unittest discover -s tests
