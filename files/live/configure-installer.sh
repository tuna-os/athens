#!/bin/bash
# Live-only integration of the same published GTK frontend Brussels ships.
set -euo pipefail
app=org.tunaos.InstallerXfce
machine_id=$(mktemp)
cp -a /etc/machine-id "$machine_id"
restore() { cp -a "$machine_id" /etc/machine-id; rm -f "$machine_id"; }
trap restore EXIT
tr -d '-' </proc/sys/kernel/random/uuid >/etc/machine-id
mkdir -p /run/dbus
# Flatpak's OCI transport uses the normal system and session buses.
dbus-daemon --system --fork --nopidfile
dbus-run-session -- bash -euo pipefail -c '
    flatpak remote-add --system --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
    flatpak remote-add --system --if-not-exists tuna-os https://tunaos.org/flatpak/tuna-os.flatpakrepo
    flatpak install --system --noninteractive --no-related tuna-os org.tunaos.InstallerXfce//master
    flatpak override --system --filesystem=/etc:ro org.tunaos.InstallerXfce
'
mkdir -p /usr/share/tunaos /usr/local/bin /etc/bootc-installer /etc/tuna-installer
# Record actual deployed commits, including dependencies; master is not a pin.
flatpak list --system --columns=ref,active,origin >/usr/share/tunaos/installer-flatpaks.tsv
flatpak info --system "$app" >/usr/share/tunaos/installer-info.txt
binary="/var/lib/flatpak/app/$app/current/active/files/bin/fisherman"
test -x "$binary"
ln -s "$binary" /usr/local/bin/fisherman
mkdir -p /usr/share/applications
cat >/usr/share/applications/athens-installer.desktop <<'EOF'
[Desktop Entry]
Name=Install TunaOS Athens
Comment=Install this Athens live media to your computer
Exec=flatpak run org.tunaos.InstallerXfce
Icon=athens-logo
Type=Application
Categories=System;
EOF
cat >/etc/bootc-installer/images.json <<'EOF'
{
  "default_image": "ghcr.io/tuna-os/athens:latest",
  "fallback_flatpaks": [],
  "images": [{
    "name": "TunaOS Athens", "imgref": "ghcr.io/tuna-os/athens:latest",
    "desc": "Experimental Pantheon desktop by TunaOS",
    "icon": "file:///usr/share/icons/hicolor/scalable/apps/athens-logo.svg",
    "bootloader": "systemd", "filesystem": "ext4", "composefs": false,
    "needs_user_creation": true, "flatpak_var_path": "state/os/default/var"
  }]
}
EOF
cp /etc/bootc-installer/images.json /etc/tuna-installer/images.json
touch /etc/bootc-installer/live-iso-mode
mkdir -p /usr/lib/systemd/system /usr/lib/tunaos/payload /var/fisherman-tmp
cat >/etc/bootc-installer/branding.json <<'EOF'
{
  "name": "TunaOS Athens",
  "id": "athens",
  "vendor": "TunaOS",
  "logo": "/usr/share/icons/hicolor/scalable/apps/athens-logo.svg",
  "default_hostname": "athens",
  "default_image": "ghcr.io/tuna-os/athens:latest"
}
EOF
cat >/usr/lib/systemd/system/usr-lib-tunaos-payload.mount <<'EOF'
[Unit]
Description=Read-only Athens installation payload
Before=display-manager.service
[Mount]
What=/usr/lib/tunaos/payload
Where=/usr/lib/tunaos/payload
Type=none
Options=bind,ro
[Install]
RequiredBy=local-fs.target
EOF
systemctl enable usr-lib-tunaos-payload.mount
mkdir -p /usr/share/polkit-1/actions
cat >/usr/share/polkit-1/actions/org.tunaos.Installer.policy <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<policyconfig>
  <action id="org.tunaos.Installer.install">
    <description>Install TunaOS Athens to disk</description>
    <message>Authentication is required to install an operating system</message>
    <defaults><allow_any>no</allow_any><allow_inactive>no</allow_inactive><allow_active>yes</allow_active></defaults>
    <annotate key="org.freedesktop.policykit.exec.path">/usr/local/bin/fisherman</annotate>
    <annotate key="org.freedesktop.policykit.exec.allow_gui">true</annotate>
  </action>
</policyconfig>
EOF
mkdir -p /etc/polkit-1/rules.d
cat >/etc/polkit-1/rules.d/90-athens-live-installer.rules <<'EOF'
polkit.addRule(function(action, subject) {
    if (action.id === "org.tunaos.Installer.install" &&
        subject.user === "liveuser" && subject.local && subject.active) {
        return polkit.Result.YES;
    }
});
EOF
