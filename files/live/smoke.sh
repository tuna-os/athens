#!/bin/bash
# Only enabled by the qualification ISO's explicit athens.smoke=1 kernel arg.
set -euo pipefail
exec >/dev/ttyS0 2>&1
finish() {
    rc=$?
    trap - EXIT
    journalctl -b -u lightdm --no-pager
    if [ "$rc" -eq 0 ]; then echo ATHENS_LIVE_SMOKE_OK; else echo ATHENS_LIVE_SMOKE_FAILED; fi
    systemctl poweroff --no-block
    exit "$rc"
}
trap finish EXIT
. /usr/lib/os-release
test "$ID" = athens
findmnt -n -t overlay /
test -s /usr/share/backgrounds/TunaOS/Athens/athens-wallpaper.png
test -s /usr/share/wayland-sessions/pantheon-wayland.desktop
for attempt in {1..120}; do
    if systemctl is-active --quiet lightdm.service; then break; fi
    sleep 1
done
systemctl is-active lightdm.service
restarts=$(systemctl show lightdm.service -p NRestarts --value)
sleep 20
systemctl is-active lightdm.service
test "$(systemctl show lightdm.service -p NRestarts --value)" = "$restarts"
# Confirm a desktop session, not merely a running display-manager process.
pgrep -u liveuser -x gala
