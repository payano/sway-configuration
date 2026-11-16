SWAY CONFIGURATION — Debian 13 och Arch Linux

Versionshanterad Sway/Waybar-miljö. De aktiva konfigurationskatalogerna är
symboliska länkar till detta repo: ändringar i ~/.config/sway eller
~/.config/dunst syns därför direkt i git diff.

INSTALLERA PÅ EN NY DATOR

  git clone <repo-url> ~/git/sway-configuration
  cd ~/git/sway-configuration
  ./install.sh --dry-run
  ./install.sh

Kör som vanlig användare, inte med sudo framför skriptet. Systemet ska redan
vara installerat, ha internet och sudo-behörighet. Installeraren använder
apt på Debian 13 och pacman på Arch. På Arch körs en full systemuppdatering
med pacman -Syu --needed. Pakethanterarens frågor och konflikter visas.

Ljudmiljön använder PipeWire, PulseAudio-kompatibilitet och WirePlumber.
Befintlig PulseAudio kan behöva ersättas. NetworkManager och Bluetooth
aktiveras för uppstart. Starta sedan om och välj Sway i inloggningsskärmen,
eller kör sway från en lokal TTY. Grafikkortsdrivrutiner, firmware och
inloggningshanterare ingår inte.

ENDAST LÄNKAR PÅ EN DATOR SOM REDAN HAR PROGRAMMEN

  ./install.sh --config-only

Detta installerar inga paket och ändrar inga tjänster. Python 3 krävs.
Korrekt installerade länkar lämnas orörda vid upprepad körning.
Standardplaceringen ~/.config krävs; XDG_CONFIG_HOME med annan sökväg stöds ej.

LÄNKADE SÖKVÄGAR

  ~/.config/sway   -> <repo>/payload/.config/sway
  ~/.config/waybar -> <repo>/payload/.config/waybar
  ~/.config/dunst  -> <repo>/payload/.config/dunst
  ~/.config/foot   -> <repo>/payload/.config/foot
  ~/.config/kanshi -> <repo>/payload/.config/kanshi

Hjälpskripten start-kanshi, save-kanshi-profile och float-chromium-notifications
länkas individuellt från ~/.local/bin till payload/.local/bin.
Övriga program och konfigurationskataloger lämnas orörda.

Repot måste finnas kvar på disk. Om du flyttar det, kör installeraren med
--config-only från den nya platsen för att uppdatera länkarna.
Det gamla tar-arkivet från exporten innehåller den tidigare kopieringsvarianten;
använd detta repo för den aktuella versionen.

ÄNDRA, COMMITTA OCH SYNKA

Redigera som vanligt ~/.config/sway/config eller ~/.config/dunst/dunstrc.
Du kan även redigera motsvarande fil i payload/ direkt; det är samma fil.

  cd ~/git/sway-configuration
  git diff
  git add payload
  git commit -m "Uppdatera skrivbordskonfiguration"
  git push

På den andra datorn, när lokala ändringar är committade:

  cd ~/git/sway-configuration
  git pull --ff-only

Ingen kopiering eller ominstallation behövs för ändringar i befintliga
konfigurationsfiler. Ladda om berört program. Super+Shift+c laddar om Sway;
logga ut/in för att starta om hela miljön. Dunst och andra processer läser
inte nödvändigtvis om filerna automatiskt.
Om paketlistorna har ändrats, kör ./install.sh igen.

För att publicera repot: skapa ett tomt repo på din Git-server och kör:

  git remote add origin <repo-url>
  git push -u origin main

DATORNS EGNA INSTÄLLNINGAR (UTANFÖR GIT)

  ~/.config/sway-local/config
  ~/.config/sway-local/kanshi-profiles/

Här ligger lokala Sway-inställningar och sparade skärmlayouter. Vid första
länkningen kopieras en eventuell äldre sway/local.conf och arbetsyterader
av typen "workspace ... output ..." till den lokala konfigurationen.
Befintliga kanshi/profiles kopieras också. Originalen finns kvar i backupen.
Befintliga sway-local-filer skrivs inte över. Annan egen konfiguration kan
hämtas från backupen och läggas i repot eller sway-local/config efter behov.

På en ny dator: ordna skärmarna med wdisplays och välj Save current layout
via högerklick på Waybars skärmikon. Profilerna sparas utanför repot.
Waybar väljer bakgrundsbelysningsenhet automatiskt.

FUNKTIONER

* Waybar längst ned: arbetsytor, klocka, systemfält, ljud, ljusstyrka,
  nätverk och batteri. Hårdvaruberoende moduler kan vara dolda.
* Wi-Fi via nm-applet, Bluetooth via Blueman.
* Ljud: vänsterklick öppnar pavucontrol, högerklick väljer ljudutgång.
* Skärmar: vänsterklick öppnar wdisplays, högerklick låter dig spara layouten.
* Svenskt tangentbord och befintliga Sway-kortkommandon.
* Super+Enter: GNOME Terminal. Super+d: programstartare.
* Print: skärmbild. Shift+Print: område. Ctrl+Alt+p: område till urklipp.
* Ctrl+Alt+l: lås. Automatiskt lås efter 5 minuter; skärmavstängning efter 6.
* Dunst och hjälpskript för flytande Chromium-notiser.

SÄKERHETSKOPIA OCH ÅTERSTÄLLNING

Befintliga kataloger/filer flyttas till en unik backup innan länkarna skapas:

  ~/.local/state/sway-portable/backups/<id>/

Äldre konfiguration och extra filer i de ersatta katalogerna finns där.
Installeraren skriver ut ett exakt återställningskommando:

  python3 deploy.py --restore "$HOME/.local/state/sway-portable/backups/<id>"

Återställning tar bort de installerade länkarna och återställer originalen.
Repot, ändringar i repot och sway-local bevaras. Paket och tjänster påverkas
inte. Om någon ersatt en länk med en annan fil/katalog avbryts återställningen.
Återställ flera installationer i omvänd ordning, och logga därefter ut/in.
Backup från gamla kopieringsinstallationen återställs med deploy.py från
commit d397e6a. Föräldrakataloger som själva är symlänkar avvisas.

NÄTVERK

Full installation avbryts om systemd-networkd, dhcpcd, ConnMan eller iwd körs,
så att konkurrerande nätverkshanterare inte införs automatiskt. iwd kan vara
en avsiktlig NetworkManager-backend; kontrollen är konservativ. Planera i så
fall migrationen lokalt eller använd --config-only när programmen finns.
Debians /etc/network/interfaces kan behöva anpassas för gränssnitt som
NetworkManager visar som unmanaged. Pakethanteraren kan starta installerade
tjänster, även om skriptet endast aktiverar dem för kommande uppstarter.

Wi-Fi-lösenord, Bluetooth-parningar, VPN-hemligheter och konton ingår inte.
Anslut och para på nytt på måldatorn. VPN-tillägg installeras separat.

KONTROLLER

  python3 -m unittest discover -s tests -v
  ./install.sh --dry-run --distro debian
  ./install.sh --dry-run --distro arch

Testerna använder temporära kataloger och verifierar länkar, redigering genom
länkar, upprepad installation, migration av lokala inställningar, rollback vid
fel och återställning. Sway-konfigurationen har validerats på Debian.
Ingen full Arch-installation eller hårdvarutest har gjorts.

Efter installation kan du kontrollera:

  systemctl status NetworkManager bluetooth
  systemctl --user status pipewire pipewire-pulse wireplumber
  nmcli device status
  pactl info
  swaymsg -t get_outputs

Paketlistor: packages.debian och packages.arch. Officiella förråd, ingen AUR.
