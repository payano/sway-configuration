SWAY PORTABLE — Debian 13 och Arch Linux

Paketet är extraherat från din Sway/Waybar-konfiguration den 16 november 2026.
Det installerar skrivbordsmiljön på ett redan installerat Debian 13 eller Arch
Linux. Kör som den vanliga användare som ska använda Sway, inte som root.
Internet och fungerande sudo-behörighet behövs för paketinstallationen.

GIT OCH VERSIONERING

Detta är ett Git-repo. Konfigurationens källfiler finns under payload/:

  payload/.config/sway/config
  payload/.config/waybar/config.jsonc
  payload/.config/waybar/style.css
  payload/.config/dunst/dunstrc
  payload/.config/foot/foot.ini
  payload/.config/kanshi/config
  payload/.local/bin/

Redigera filerna i repot och behåll platshållaren @HOME@ i sökvägar.
Installeraren ersätter den med den aktuella användarens hemkatalog.
Filerna kopieras vid installation; ändringar direkt under ~/.config synkas
inte automatiskt tillbaka till repot. Lägg gemensamma ändringar i payload/.
Behåll maskinspecifika ändringar i ~/.config/sway/local.conf.

Efter ändringar i repot:

  git diff
  ./install.sh --config-only
  git add payload
  git commit -m "Uppdatera skrivbordskonfiguration"

Logga ut/in för att starta om hela miljön med den nya konfigurationen.
Super+Shift+c laddar om Sway-konfigurationen, men startar inte om alla program.

För att lägga repot på din Git-server, skapa ett tomt repo där och kör:

  git remote add origin <repo-url>
  git push -u origin main

På en annan dator:

  git clone <repo-url> sway-portable
  cd sway-portable
  ./install.sh --dry-run
  ./install.sh

För att hämta och tillämpa senare konfigurationsändringar:

  git pull --ff-only
  ./install.sh --config-only

Om paketlistorna har ändrats, kör ./install.sh i stället för --config-only.
Inga lösenord, Bluetooth-parningar eller maskinspecifika skärmprofiler ingår.

INSTALLERA FRÅN ARKIV (ALTERNATIV TILL GIT CLONE)

  tar -xzf sway-portable.tar.gz
  cd sway-portable
  ./install.sh --dry-run
  ./install.sh

Starta om och välj Sway i inloggningsskärmen. Om du inte har en grafisk
inloggningshanterare: logga in på en lokal TTY och kör sway.
Ingen inloggningshanterare eller grafikkortsdrivrutin installeras av paketet.

Distributionen identifieras automatiskt genom /etc/os-release.
Debian: apt-get update och apt-get install.
Arch: pacman -Syu --needed, vilket även uppdaterar hela systemet.
Pakethanterarens egna frågor visas, inklusive eventuella paketkonflikter.
Ljudmiljön använder PipeWire med PulseAudio-kompatibilitet och WirePlumber.
En befintlig PulseAudio-installation kan därför behöva ersättas.

FÖRHANDSGRANSKA / ENDAST KONFIGURATION

  ./install.sh --dry-run --distro debian
  ./install.sh --dry-run --distro arch
  ./install.sh --config-only

--config-only kopierar konfigurationen och kräver python3, men installerar inga
paket och ändrar inga tjänster. Använd bara detta när beroendena redan finns.

FUNKTIONER

* Waybar längst ned med arbetsytor, klocka, systemfält, ljud, ljusstyrka,
  nätverk och batteri. Moduler för hårdvara som saknas kan vara dolda.
* Wi-Fi: nm-applet i systemfältet. Klick på nätverkstexten öppnar anslutningar.
* Bluetooth: Blueman i systemfältet.
* Ljud: vänsterklick öppnar pavucontrol, högerklick väljer ljudutgång.
* Skärmar: vänsterklick på skärmikonen öppnar wdisplays. Högerklick och
  "Save current layout" sparar layouten för automatisk växling med Kanshi.
* Svenskt tangentbord och dina befintliga Sway-kortkommandon.
* Super+Enter: GNOME Terminal. Super+d: programstartare.
* Print: skärmbild. Shift+Print: område. Ctrl+Alt+p: område till urklipp.
* Ctrl+Alt+l: lås. Automatiskt lås efter 5 minuter och skärmavstängning efter 6.
* Dunst-notiser och ditt skript för flytande Chromium-notiser.

ANPASSNINGAR FÖR ANDRA DATORER

Användarsökvägar skapas vid installationen. Inga referenser till den gamla
användarens hemkatalog behöver redigeras. Hemkataloger med mellanslag eller
shell-specialtecken stöds inte. Standardplacering ~/.config krävs.

De gamla skärmportarna DP-8, DP-6 och eDP-1 och deras arbetsytemappning har
inte aktiverats. Gamla skärmprofiler exporteras inte. Ställ in skärmarna i
wdisplays och spara via panelen på den nya datorn. Befintliga Kanshi-profiler
på måldatorn bevaras; se över dem om du installerar över en äldre miljö.

Waybar väljer bakgrundsbelysningsenhet automatiskt i stället för att kräva
intel_backlight. Gör eventuella maskinspecifika Sway-inställningar i:

  ~/.config/sway/local.conf

Den filen bevaras vid ominstallation. Övriga medföljande konfigurationsfiler
ersätts efter säkerhetskopiering. Generell XDG-autostart har ersatts med
explicit start av panelens program för att undvika dubbla applets. Egna
autostartprogram kan läggas till i local.conf.

NÄTVERK OCH TJÄNSTER

NetworkManager och Bluetooth aktiveras för kommande uppstarter. Installeraren
startar inte om nätverket under den pågående sessionen. Pakethanteraren kan
själv starta nyinstallerade tjänster, särskilt på Debian.
PipeWire-sockets och WirePlumber aktiveras för användaren.

Om systemd-networkd, dhcpcd, ConnMan eller iwd körs avbryts full installation
före paketändringar. Planera då övergången till NetworkManager lokalt på
datorn; stäng inte av din enda nätverksanslutning blint. iwd kan även vara en
avsiktlig NetworkManager-backend, så denna kontroll är konservativ.
Befintlig Debian-konfiguration i /etc/network/interfaces kan också behöva
anpassas om gränssnittet visas som "unmanaged" i nmcli device status.

Wi-Fi-lösenord, VPN-hemligheter, Bluetooth-parningar, nyckelringar och andra
konton exporteras inte. Anslut och para på nytt på måldatorn. Eventuella
VPN-tillägg och hårdvaruspecifik firmware installeras separat vid behov.

SÄKERHETSKOPIA OCH ÅTERSTÄLLNING

Befintliga berörda filer säkerhetskopieras innan konfigurationen skrivs:

  ~/.local/state/sway-portable/backups/<tid-och-unikt-id>/

Installeraren skriver ut ett exakt återställningskommando, till exempel:

  python3 deploy.py --restore "$HOME/.local/state/sway-portable/backups/<id>"

Återställning tar bort filer som skapades av den installationen och lägger
tillbaka tidigare filer. Senare ändringar i dessa filer skrivs över. Återställ
flera installationer i omvänd ordning. Paket och systemtjänster återställs
inte. Logga ut/in efter återställningen. Symlänkar i destinationskataloger
avvisas för att inte oavsiktligt skriva i ett dotfiles-repository.

VERIFIERING

Utfört: Bash/sh/Python-syntax, båda distributionernas förhandsgranskning,
installation i tillfällig hemkatalog, upprepad installation, bevarande av
local.conf, återställning samt Sways konfigurationsvalidering på Debian.
Ingen riktig paketinstallation har körts av exportarbetet. Arch-session och
Bluetooth/Wi-Fi/ljud/skärmar måste funktionstestas på måldatorn.

Efter installation, kontrollera exempelvis:

  systemctl status NetworkManager bluetooth
  systemctl --user status pipewire pipewire-pulse wireplumber
  nmcli device status
  pactl info
  swaymsg -t get_outputs

Paketnamn finns i packages.debian och packages.arch och kan granskas före
installation. Installeraren använder officiella paketförråd, ingen AUR.
Referenser:
https://packages.debian.org/trixie/wmenu
https://packages.debian.org/trixie/wdisplays
https://packages.debian.org/trixie/lxqt-policykit
https://archlinux.org/packages/extra/x86_64/wmenu/
https://archlinux.org/packages/extra/x86_64/network-manager-applet/
https://archlinux.org/packages/extra/x86_64/lxqt-policykit/
