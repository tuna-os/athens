#!/bin/sh
# Fail when an image root carries a development access default: an account
# that needs no password, a root password baked into the image, passwordless
# sudo, or a login that happens by itself.
#
# Usage: check-image-access.sh [ROOT]    (ROOT defaults to /)
set -eu

root="${1:-/}"
root="${root%/}"
status=0

fail() {
    echo "access check: $*" >&2
    status=1
}

# has FILE REGEX: true when a line of FILE that is not a comment matches REGEX.
has() {
    [ -f "$1" ] && grep -v '^[[:space:]]*#' "$1" | grep -Eq -- "$2"
}

# /etc as shipped, plus the two places an image keeps the copy that seeds it.
for etc in etc usr/etc usr/share/factory/etc; do
    dir="$root/$etc"

    if [ -f "$dir/shadow" ]; then
        while IFS=: read -r user hash _ || [ -n "$user" ]; do
            [ -n "$user" ] || continue
            [ -n "$hash" ] || fail "/$etc/shadow: '$user' has an empty password"
        done < "$dir/shadow"
    fi

    if has "$dir/group" '^nopasswdlogin:[^:]*:[^:]*:.'; then
        fail "/$etc/group: nopasswdlogin has members"
    fi

    for file in "$dir/sudoers" "$dir"/sudoers.d/*; do
        if has "$file" 'NOPASSWD'; then
            fail "${file#"$root"}: NOPASSWD rule"
        fi
    done

    for file in "$dir/lightdm/lightdm.conf" "$dir"/lightdm/lightdm.conf.d/*; do
        if has "$file" '^[[:space:]]*autologin-user[[:space:]]*=[[:space:]]*[^[:space:]]'; then
            fail "${file#"$root"}: display manager autologin"
        fi
    done

    if has "$dir/gdm/custom.conf" '^[[:space:]]*AutomaticLoginEnable[[:space:]]*=[[:space:]]*[Tt]rue'; then
        fail "/$etc/gdm/custom.conf: display manager autologin"
    fi
done

for file in "$root"/usr/share/lightdm/lightdm.conf.d/*; do
    if has "$file" '^[[:space:]]*autologin-user[[:space:]]*=[[:space:]]*[^[:space:]]'; then
        fail "${file#"$root"}: display manager autologin"
    fi
done

for file in "$root"/usr/lib/systemd/system/*getty*.d/* "$root"/etc/systemd/system/*getty*.d/*; do
    if has "$file" '--autologin'; then
        fail "${file#"$root"}: console autologin"
    fi
done

# systemd sets the root password from these credentials at boot, so one stored
# in the image gives every machine the same password. Mkosi's RootPassword=
# writes passwd.hashed-password.root here.
for file in "$root"/usr/lib/credstore/passwd.*password.root "$root"/etc/credstore/passwd.*password.root; do
    if [ -e "$file" ]; then
        fail "${file#"$root"}: root password stored in the image"
    fi
done

if [ "$status" -eq 0 ]; then
    echo "access check: no development access defaults in ${root:-/}"
fi
exit "$status"
