#!/usr/bin/env python3
"""Athens-only external AT-SPI driver for the unmodified shipped GTK installer.

Credentials arrive through stdin only. Stdout is a bounded safe-state protocol,
never an accessibility tree, recipe, password, application log or screenshot.
All actions use real exported widgets. No frontend imports or test/dry-run API.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import time

credentials = json.loads(sys.stdin.readline())
mode = credentials["mode"]


def wait_for(function, timeout=120):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        value = function()
        if value:
            return value
        time.sleep(0.25)
    raise RuntimeError("required real UI state did not become available")


def session_environment():
    pids = subprocess.run(["pgrep", "-u", str(os.getuid()), "-x", "gala"], capture_output=True, text=True)
    if pids.returncode:
        return False
    for pid in pids.stdout.split():
        values = dict(item.split(b"=", 1) for item in Path(f"/proc/{pid}/environ").read_bytes().split(b"\0") if b"=" in item)
        if values.get(b"WAYLAND_DISPLAY"):
            for key in ("DBUS_SESSION_BUS_ADDRESS", "WAYLAND_DISPLAY", "XDG_RUNTIME_DIR", "XDG_CURRENT_DESKTOP", "XDG_SESSION_TYPE", "XDG_SESSION_ID", "XDG_SESSION_CLASS", "DISPLAY", "AT_SPI_BUS_ADDRESS"):
                if key.encode() in values:
                    os.environ[key] = values[key.encode()].decode()
            return True
    return False


wait_for(session_environment)
import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi


def walk(node):
    yield node
    for index in range(node.get_child_count()):
        child = node.get_child_at_index(index)
        if child is not None:
            yield from walk(child)


def visible(node):
    return node.get_state_set().contains(Atspi.StateType.SHOWING)


def frame():
    for node in walk(Atspi.get_desktop(0)):
        if node.get_role() == Atspi.Role.FRAME and visible(node):
            if mode == "live" and node.get_name() == "TunaOS Athens Installer":
                return node
            if mode == "greeter":
                return node
    return False


def nodes():
    root = frame()
    return [node for node in walk(root) if visible(node)] if root else []


def named(name):
    return next((node for node in nodes() if node.get_name().casefold() == name.casefold()), None)


def page(title):
    return wait_for(lambda: named(title))


def action(node):
    interface = node.get_action_iface()
    if interface is None or not node.get_state_set().contains(Atspi.StateType.SENSITIVE):
        return False
    return interface.do_action(0)


def press(name):
    wait_for(lambda: (node := named(name)) is not None and action(node))


def entries():
    return [node for node in nodes() if node.get_state_set().contains(Atspi.StateType.EDITABLE)]


def empty_fields(fields):
    return all(node.get_text_iface().get_text(0, -1) == "" for node in fields)


def fill(fields, values):
    if len(fields) != len(values):
        raise RuntimeError("published GUI field structure differs from the inspected source")
    for field, value in zip(fields, values):
        if not field.get_editable_text_iface().set_text_contents(value):
            raise RuntimeError("real GUI rejected editable text input")


def event(stage, **data):
    print(json.dumps({"stage": stage, **data}), flush=True)
    if json.loads(sys.stdin.readline()).get("continue") is not True:
        raise RuntimeError("host did not acknowledge safe UI stage")


def state():
    result = subprocess.check_output(["python3", "/usr/libexec/athens-defaults-state", "--nonce", credentials["nonce"]], text=True)
    return json.loads(result.split("ATHENS_DEFAULTS_STATE=", 1)[1])


def live():
    event("live-desktop", state=state())
    app = "org.tunaos.InstallerXfce"
    subprocess.Popen(["flatpak", "run", app], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    page("Welcome to TunaOS Athens")
    event("installer-welcome")
    # The host has run the pinned EMPTY-form HMP walkthrough. Restart the same
    # published app to reset navigation, never its implementation or defaults.
    subprocess.run(["flatpak", "kill", app], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.Popen(["flatpak", "run", app], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    page("Welcome to TunaOS Athens")
    press("Get started")
    page("What do you want to install?")
    press("TunaOS Athens")  # Catalog leaf, not the unrelated live-system default.
    event("installer-source")
    press("Next")
    page("Where should TunaOS Athens be installed?")
    radios = [node for node in nodes() if node.get_role() == Atspi.Role.RADIO_BUTTON and "/dev/vda" in node.get_name()]
    if len(radios) != 1 or not action(radios[0]):
        raise RuntimeError("the one disposable target disk is not exposed by the shipped GUI")
    event("installer-disk")
    press("Next")
    page("Disk encryption")
    press("Passphrase")
    fields = entries()
    if len(fields) != 2 or not empty_fields(fields):
        raise RuntimeError("refusing a screenshot of a populated or unexpected credential form")
    event("installer-encryption")
    # No event/capture is permitted from here until the real summary is proven.
    fill(fields, [credentials["luks"], credentials["luks"]])
    press("Next")
    page("Name this computer")
    fill(entries(), ["athens-qualification", credentials["username"], credentials["fullname"], credentials["password"]])
    press("Next")
    page("Confirm installation")
    if entries():
        raise RuntimeError("credential controls remain visible at the summary")
    summary = "\n".join(node.get_name() for node in nodes() if node.get_role() == Atspi.Role.LABEL)
    if "/dev/vda" not in summary or "Passphrase" not in summary:
        raise RuntimeError("GUI summary did not retain the encrypted disposable-disk selection")
    event("installer-summary")
    press("Install now")
    wait_for(lambda: named("TunaOS Athens is installed"), timeout=3600)
    if entries():
        raise RuntimeError("a credential control remains visible on the completion page")
    event("installer-done")


def greeter():
    wait_for(frame)
    password_fields = lambda: [node for node in nodes() if node.get_role() == Atspi.Role.PASSWORD_TEXT]
    if not password_fields():
        label = wait_for(lambda: named(credentials["fullname"]) or named(credentials["username"]))
        for _ in range(5):
            if action(label):
                break
            label = label.get_parent()
    fields = wait_for(password_fields)
    if len(fields) != 1 or not empty_fields(fields):
        raise RuntimeError("greeter is not at an empty password field")
    event("installed-greeter")
    fill(fields, [credentials["password"]])
    event("submit-login")  # Host sends Return, without enabling capture.


def session():
    if os.environ.get("XDG_SESSION_CLASS", "user") != "user":
        raise RuntimeError("not an actual installed user session")
    event("installed-desktop", state=state())
    subprocess.Popen(["gio", "open", "settings://about/os"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    def about():
        for node in walk(Atspi.get_desktop(0)):
            if visible(node) and "TunaOS Athens" in node.get_name() and node.get_role() == Atspi.Role.LABEL:
                return node
        return False
    wait_for(about)
    event("installed-about")


try:
    {"live": live, "greeter": greeter, "session": session}[mode]()
except Exception:
    # Never print exception values, widget text, input, or a credential tree.
    print(json.dumps({"stage": "failed", "reason": "native-gui-state-or-action-failed"}), flush=True)
    sys.exit(1)
