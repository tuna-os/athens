#!/usr/bin/env python3
"""Read-only Athens desktop-default receipt, run in the actual logged-in session.

Never sets a setting, resets a user value, or includes credentials. The visual
journey binds this line to its fresh nonce and corresponding VM/boot.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

from gi.repository import Gio

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--nonce", required=True)
args = parser.parse_args()
background = Gio.Settings.new("org.gnome.desktop.background")
keys = ("picture-uri", "picture-uri-dark", "picture-options")
bootc = subprocess.run(["bootc", "status", "--json"], capture_output=True, text=True)
if bootc.returncode:
    bootc = subprocess.run(["sudo", "-n", "bootc", "status", "--json"], capture_output=True, text=True)
print("ATHENS_DEFAULTS_STATE=" + json.dumps({
    "nonce": args.nonce,
    "boot_id": Path("/proc/sys/kernel/random/boot_id").read_text().strip(),
    "desktop": os.environ.get("XDG_CURRENT_DESKTOP", ""),
    "session_type": os.environ.get("XDG_SESSION_TYPE", ""),
    "uid": os.getuid(),
    "os_release": Path("/usr/lib/os-release").read_text(),
    "bootc": json.loads(bootc.stdout) if bootc.returncode == 0 else {"unavailable": True, "exit": bootc.returncode},
    "dconf_profile": os.environ.get("DCONF_PROFILE", "user"),
    "schema_directory_override": os.environ.get("GSETTINGS_SCHEMA_DIR", ""),
    "settings_backend_override": os.environ.get("GSETTINGS_BACKEND", ""),
    "compiled_schemas_sha256": hashlib.sha256(Path("/usr/share/glib-2.0/schemas/gschemas.compiled").read_bytes()).hexdigest(),
    "artwork_sha256": {
        "athens-wallpaper.png": hashlib.sha256(Path("/usr/share/backgrounds/TunaOS/Athens/athens-wallpaper.png").read_bytes()).hexdigest(),
        "athens-logo.svg": hashlib.sha256(Path("/usr/share/icons/hicolor/scalable/apps/athens-logo.svg").read_bytes()).hexdigest(),
    },
    "background": {key: {
        "effective": background.get_value(key).unpack(),
        "default": background.get_default_value(key).unpack(),
        "user": value.unpack() if (value := background.get_user_value(key)) is not None else None,
        "writable": background.is_writable(key),
    } for key in keys},
}, sort_keys=True), flush=True)
