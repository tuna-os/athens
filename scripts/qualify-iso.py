#!/usr/bin/env python3
"""Qualify real Athens GTK GUI, LUKS and fresh-session branding in QEMU.

Default CI mode drives the unmodified published GTK frontend through AT-SPI.
Optional --manual uses a VNC operator. Neither path substitutes a CLI install,
fixture, private installer binary, secret recipe or wallpaper-setting command.
The pinned TunaOS engines judge actual safe-state frames, never credential
entry. The automatic path uses a restricted host-only SSH control transport.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import select
import shlex
import secrets
import socket
import subprocess
import sys
import tempfile
import time
import uuid

PIN = "0b577a9eb2d83b49eecbaf25d083f458e003e70b"
ROOT = Path(__file__).resolve().parents[1]
ASSETS = ("athens-wallpaper.png", "athens-logo.svg", "athens-boot-logo.png")


def run(*args, **kwargs):
    return subprocess.run(args, check=True, **kwargs)


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args])


def confirm(instruction, token="READY"):
    print(f"\n{instruction}\nType {token} only when that safe state is visible.", flush=True)
    if input("> ").strip() != token:
        raise RuntimeError("operator did not confirm the required safe state")


class VM:
    def __init__(self, out, firmware, variables, iso=None, ssh_port=None):
        self.out = out
        self.qmp_path = out / "qmp.sock"
        self.hmp_path = out / "hmp.sock"
        self.vnc_path = out / "vnc.sock"
        self.safe = False
        self.process = None
        self.serial = None
        self.iso = iso
        self.firmware = firmware
        self.variables = variables
        self.ssh_port = ssh_port

    def start(self):
        for path in (self.qmp_path, self.hmp_path, self.vnc_path):
            path.unlink(missing_ok=True)
        self.serial = (self.out / ("live-serial.log" if self.iso else "installed-serial.log")).open("a")
        acceleration = "kvm" if os.access("/dev/kvm", os.R_OK | os.W_OK) else "tcg"
        command = ["qemu-system-x86_64", "-machine", f"q35,accel={acceleration}",
                   "-m", "6144", "-smp", "4", "-display", "none", "-no-reboot",
                   "-device", "virtio-vga,xres=1920,yres=1080",
                   "-nic", (f"user,model=virtio-net-pci,restrict=on,hostfwd=tcp:127.0.0.1:{self.ssh_port}-:22"
                            if self.ssh_port else "none"),
                   "-serial", "stdio", "-qmp", f"unix:{self.qmp_path},server=on,wait=off",
                   "-monitor", f"unix:{self.hmp_path},server=on,wait=off",
                   "-vnc", f"unix:{self.vnc_path}",
                   "-drive", f"if=pflash,format=raw,readonly=on,file={self.firmware}",
                   "-drive", f"if=pflash,format=raw,file={self.variables}",
                   "-drive", f"if=virtio,format=raw,file={self.out / 'disk.raw'}"]
        if self.iso:
            command += ["-drive", f"if=none,id=live,format=raw,media=cdrom,readonly=on,file={self.iso}",
                        "-device", "virtio-scsi-pci,id=scsi", "-device", "scsi-cd,drive=live", "-boot", "d"]
        self.process = subprocess.Popen(command, stdout=self.serial, stderr=subprocess.STDOUT)
        for _ in range(120):
            if self.process.poll() is not None:
                raise RuntimeError("QEMU exited before opening its monitor")
            if self.qmp_path.exists():
                break
            time.sleep(0.5)
        else:
            raise RuntimeError("QEMU did not open its monitor")
        print(f"Open remote-viewer vnc+unix://{self.vnc_path}", flush=True)
        return {"pid": self.process.pid,
                "start_ticks": Path(f"/proc/{self.process.pid}/stat").read_text().split()[21],
                "external_network": "disabled", "control_nic": bool(self.ssh_port),
                "iso_attached": bool(self.iso)}

    def qmp(self, command, arguments=None):
        with socket.socket(socket.AF_UNIX) as sock:
            sock.settimeout(30)
            sock.connect(str(self.qmp_path))
            stream = sock.makefile("rwb")
            json.loads(stream.readline())
            for request in ({"execute": "qmp_capabilities"},
                            {"execute": command, "arguments": arguments or {}}):
                stream.write(json.dumps(request).encode() + b"\n")
                stream.flush()
                while True:
                    response = json.loads(stream.readline())
                    if "error" in response:
                        raise RuntimeError(f"QMP failed: {response['error']}")
                    if "return" in response:
                        result = response["return"]
                        break
            return result

    def capture(self, name, receipt):
        if not self.safe:
            raise RuntimeError("capture forbidden during credential entry or an unconfirmed state")
        if self.process.poll() is not None:
            raise RuntimeError("cannot capture an exited VM")
        path = self.out / f"{name}.png"
        if path.exists():
            raise RuntimeError("refusing to overwrite a prior frame")
        self.qmp("screendump", {"filename": str(path), "format": "png"})
        receipt["frames"][name] = {"sha256": sha(path), "captured_at_ns": time.time_ns(),
                                   "vm_pid": self.process.pid}

    def stop(self):
        self.safe = False
        if self.process is not None and self.process.poll() is None:
            try:
                self.qmp("quit")
            except (OSError, ValueError, RuntimeError):
                self.process.terminate()
            try:
                self.process.wait(timeout=30)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
        if self.serial:
            self.serial.close()
        for path in (self.qmp_path, self.hmp_path, self.vnc_path):
            path.unlink(missing_ok=True)


def stage_engine(contract, engine, commit):
    if git(contract, "rev-parse", "HEAD").decode().strip() != PIN:
        raise RuntimeError(f"visual contract must be pinned to {PIN}")
    # Export only the existing engines, unmodified, from their pinned Git blobs.
    # Independent approved assets come from THIS committed source, not the guest.
    for script in ("install-checkpoints.py", "installer-walkthrough.py"):
        target = engine / "scripts" / script
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(git(contract, "show", f"{PIN}:scripts/{script}"))
    for asset in ASSETS:
        target = engine / "branding/athens" / asset
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(git(ROOT, "show", f"{commit}:branding/athens/{asset}"))


def defaults_state(vm, phase, receipt):
    nonce = uuid.uuid4().hex
    vm.safe = False
    confirm("Open a terminal in the actual Pantheon session and run:\n"
            f"python3 /usr/libexec/athens-defaults-state --nonce {nonce} | sudo tee /dev/ttyS0\n"
            "Enter any sudo password directly in VNC. Close the terminal afterwards.\n"
            "Do NOT change wallpaper, theme, dconf values, or schema files.", "STATE-READY")
    log = vm.out / ("live-serial.log" if phase == "live" else "installed-serial.log")
    states = []
    for line in log.read_text(errors="replace").splitlines():
        if line.startswith("ATHENS_DEFAULTS_STATE="):
            state = json.loads(line.split("=", 1)[1])
            if state.get("nonce") == nonce:
                states.append(state)
    if len(states) != 1:
        raise RuntimeError("missing or duplicate actual-session state receipt")
    validate_state(states[0], phase, receipt)
    vm.safe = True


def validate_state(state, phase, receipt):
    if "Pantheon" not in state["desktop"].split(":") or state["session_type"] != "wayland":
        raise RuntimeError("receipt was not collected in the actual Pantheon Wayland session")
    if 'ID="athens"' not in state["os_release"] or 'NAME="TunaOS Athens"' not in state["os_release"]:
        raise RuntimeError("the booted OS is not Athens")
    if state["dconf_profile"] != "user" or state["schema_directory_override"] or state["settings_backend_override"] not in ("", "dconf"):
        raise RuntimeError("receipt used a nonstandard test settings profile/schema directory/backend")
    if set(state["artwork_sha256"]) != {"athens-wallpaper.png", "athens-logo.svg"}:
        raise RuntimeError("receipt did not bind both canonical desktop identity assets")
    for asset, digest in state["artwork_sha256"].items():
        expected_asset = hashlib.sha256(git(
            ROOT, "show", f"{receipt['source']['source_commit']}:branding/athens/{asset}")).hexdigest()
        if digest != expected_asset:
            raise RuntimeError("guest artwork does not belong to the exact committed source")
    if phase == "installed":
        booted = state["bootc"].get("status", {}).get("booted") or {}
        digest = (booted.get("image") or {}).get("imageDigest")
        if digest != receipt["source"]["payload_manifest_digest"]:
            raise RuntimeError("installed bootc digest is not the exact embedded candidate")
    expected = {"picture-uri": "file:///usr/share/backgrounds/TunaOS/Athens/athens-wallpaper.png",
                "picture-uri-dark": "file:///usr/share/backgrounds/TunaOS/Athens/athens-wallpaper.png",
                "picture-options": "zoom"}
    for key, value in expected.items():
        row = state["background"][key]
        if row["effective"] != value or row["default"] != value or row["user"] is not None or not row["writable"]:
            raise RuntimeError(f"{phase}: {key} is not an effective unlocked fresh-user default")
    if phase == "installed" and state["boot_id"] == receipt["states"]["live"]["boot_id"]:
        raise RuntimeError("installed receipt reused the live boot")
    receipt["states"][phase] = state


def judge(engine, out, spec, label):
    result = out / f"{label}.json"
    sheet = out / f"{label}.png"
    with (out / f"{label}.tap").open("w") as log:
        run(sys.executable, str(engine / "scripts/install-checkpoints.py"), str(out),
            "--flavor", "pantheon", "--variant", "athens", "--spec", str(spec),
            "--strict", "--json", str(result), "--sheet", str(sheet), stdout=log, stderr=subprocess.STDOUT)
    doc = json.loads(result.read_text())
    if not sheet.is_file() or doc.get("outcome") != "passed" or not doc.get("pixels_enforced"):
        raise RuntimeError("checkpoint output/contact sheet is absent or not fully enforced")
    rows = doc.get("checkpoints", [])
    if not rows or any(row.get("required") and row.get("outcome") != "passed" for row in rows):
        raise RuntimeError("a required checkpoint is unproven")
    return doc


def encrypted_disk(out):
    loop = subprocess.check_output(["losetup", "--find", "--show", "--partscan", str(out / "disk.raw")], text=True).strip()
    try:
        run("udevadm", "settle")
        data = json.loads(subprocess.check_output(["lsblk", "--json", "--fs", loop], text=True))
        partitions = data["blockdevices"][0].get("children", [])
        encrypted = [row for row in partitions if row.get("fstype") == "crypto_LUKS"]
        if len(encrypted) != 1:
            raise RuntimeError("real GUI installation did not produce exactly one LUKS root partition")
        return {"partitions": [{key: row.get(key) for key in ("name", "fstype", "uuid", "label")} for row in partitions],
                "luks_uuid": encrypted[0]["uuid"]}
    finally:
        run("losetup", "--detach", loop)


def prepare_controls(engine, control_root):
    """Export genuine other-city artwork from independent committed sources."""
    from urllib.parse import quote
    from urllib.request import urlopen

    controls = []
    for city, repository, logo, wallpaper in (
            ("brussels", "xfce-linux", "brussels-logo.svg", "brussels-wallpaper.png"),
            ("tromso", "tromso", "tromso-logo.svg", "tromso-wallpaper.png")):
        source = control_root / repository
        commit = git(source, "rev-parse", "HEAD").decode().strip()
        for kind, filename in (("logo", logo), ("wallpaper", wallpaper)):
            relative = f"branding/{city}/{filename}"
            data = git(source, "show", f"{commit}:{relative}")
            target = engine / "branding/controls" / filename
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            controls.append({"id": f"{city}-{kind}", "kind": kind,
                             "asset": str(target.relative_to(engine)),
                             "source": f"https://github.com/tuna-os/{repository}@{commit}:{relative}",
                             "sha256": hashlib.sha256(data).hexdigest()})
    upstream = (
        ("upstream-logo", "logo", "gnome-boot-logo.png",
         "https://gitlab.gnome.org/GNOME/gnome-build-meta/-/raw/8a89846df11e86cee57c728a86a247e61d604b84/files/plymouth/gnome-boot-logo.png"),
        ("upstream-wallpaper", "wallpaper", "elementary-default.jpg",
         "https://raw.githubusercontent.com/elementary/wallpapers/2ae7f028a7d807864bdc6b28947d5eb3f36add61/backgrounds/" +
         quote("A Large Body of Water Surrounded By Mountains.jpg")),
    )
    for name, kind, filename, url in upstream:
        local = list(ROOT.glob(".bst/staged-junctions/gnome-build-meta.bst/*/files/plymouth/gnome-boot-logo.png"))
        if name == "upstream-logo" and local:
            data = local[0].read_bytes()
        else:
            with urlopen(url, timeout=90) as response:
                data = response.read()
        if name == "upstream-logo":
            if hashlib.sha256(data).hexdigest() != "a95912d39315a5d0b64d2f015c913fd6988ac03ed0bcf942531d881103af3183":
                raise RuntimeError("original upstream GNOME logo does not match its pinned source")
        elif hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest() != "a2e15e1b41239b8b378ec2042b6a7ee1ce0262d7":
            raise RuntimeError("original upstream wallpaper does not match its pinned Git blob")
        target = engine / "branding/controls" / filename
        target.write_bytes(data)
        controls.append({"id": name, "kind": kind, "asset": str(target.relative_to(engine)),
                         "source": url, "sha256": hashlib.sha256(data).hexdigest()})
    return controls


def negative_controls(engine, out, spec, frames, artwork_controls):
    """Mutate this run's real evidence; reject actual other-city/upstream art."""
    import yaml

    verdicts = {}
    by_name = {row["id"]: row for row in artwork_controls}
    for control in ("wrong-name", "stale", "missing-frame", "missing-ocr", *by_name):
        with tempfile.TemporaryDirectory(prefix=f"athens-{control}-") as temporary:
            work = Path(temporary)
            for name in frames:
                shutil.copyfile(out / f"{name}.png", work / f"{name}.png")
            document = yaml.safe_load(spec.read_text())
            if control == "wrong-name":
                document["checkpoints"][1]["keywords"] = ["DefinitelyNotAthens"]
            elif control == "stale":
                shutil.copyfile(work / "installed-greeter.png", work / "installed-desktop.png")
            elif control == "missing-frame":
                (work / "live-desktop.png").unlink()
            elif control in by_name:
                bad = by_name[control]
                for checkpoint in document["checkpoints"]:
                    for region in checkpoint.get("regions", []):
                        if (bad["kind"] == "wallpaper" and region["id"] == "wallpaper") or (
                                bad["kind"] == "logo" and region["id"] in ("logo", "watermark")):
                            region["artwork"]["asset"] = bad["asset"]
            local_spec = work / "contract.yaml"
            local_spec.write_text(yaml.safe_dump(document))
            environment = os.environ.copy()
            if control == "missing-ocr":
                environment["PATH"] = str(work / "no-tools")
            result = subprocess.run([
                sys.executable, str(engine / "scripts/install-checkpoints.py"), str(work),
                "--flavor", "pantheon", "--variant", "athens", "--spec", str(local_spec),
                "--strict", "--json", str(work / "result.json"),
                "--sheet", str(work / "sheet.png"),
            ], env=environment, capture_output=True, text=True)
            (out / f"control-{control}.tap").write_text(result.stdout + result.stderr)
            expected = result.returncode == 77 if control == "missing-ocr" else 0 < result.returncode < 77
            if control in by_name:
                result_doc = json.loads((work / "result.json").read_text())
                # A missing/undecodable reference is NOT proof that wrong art
                # was distinguished. The actual artwork-distance check must fail.
                expected = expected and any(
                    region.get("reason") == "artwork-mismatch"
                    for checkpoint in result_doc.get("checkpoints", [])
                    for region in checkpoint.get("regions", []))
            verdicts[control] = {"exit": result.returncode, "rejected": bool(expected)}
            if not expected:
                raise RuntimeError(f"negative control did not reject {control}: exit {result.returncode}")
    (out / "negative-controls.json").write_text(json.dumps(verdicts, indent=2) + "\n")
    return verdicts


class GuestDriver:
    """One bounded SSH/AT-SPI session; credentials only travel over stdin."""
    def __init__(self, port, credentials, code, key=None, greeter=False):
        self.credentials = credentials
        self.password_auth = key is None
        self.ssh = ["ssh", "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null",
                    "-o", "LogLevel=ERROR", "-o", "ConnectTimeout=5", "-p", str(port)]
        if key:
            self.ssh += ["-i", str(key), "-o", "BatchMode=yes", "liveuser@127.0.0.1"]
        else:
            self.ssh += ["-o", "PreferredAuthentications=password",
                         "-o", "PubkeyAuthentication=no", f"{credentials['username']}@127.0.0.1"]
        self.remote = ["python3", "-u", "-c", code]
        if greeter:
            self.remote = ["sudo", "-n", "runuser", "-u", "lightdm", "--", *self.remote]
        self.process = None

    def spawn(self, command, **kwargs):
        if not self.password_auth:
            return subprocess.Popen([*self.ssh, *command], **kwargs)
        read_fd, write_fd = os.pipe()
        try:
            os.write(write_fd, (self.credentials["password"] + "\n").encode())
        finally:
            os.close(write_fd)
        try:
            return subprocess.Popen(["sshpass", "-d", str(read_fd), *self.ssh, *command],
                                    pass_fds=(read_fd,), **kwargs)
        finally:
            os.close(read_fd)

    def start(self, timeout=300):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            probe = self.spawn(["true"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            try:
                status = probe.wait(timeout=10)
            except subprocess.TimeoutExpired:
                probe.kill()
                probe.wait()
                status = 1
            if status == 0:
                break
            time.sleep(2)
        else:
            raise RuntimeError("guest control transport did not become ready")
        self.process = self.spawn([shlex.join(self.remote)], stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        self.process.stdin.write(json.dumps(self.credentials) + "\n")
        self.process.stdin.flush()

    def receive(self, stage, timeout=180):
        ready, _, _ = select.select([self.process.stdout], [], [], timeout)
        if not ready:
            raise RuntimeError(f"native GUI timed out waiting for {stage}")
        line = self.process.stdout.readline()
        try:
            data = json.loads(line)
        except ValueError:
            raise RuntimeError("native GUI protocol ended or returned an invalid safe-state receipt") from None
        if data.get("stage") != stage:
            raise RuntimeError(f"native GUI did not prove required stage {stage}")
        return data

    def acknowledge(self):
        self.process.stdin.write('{"continue": true}\n')
        self.process.stdin.flush()

    def stop(self):
        if self.process is not None:
            if self.process.stdin:
                try:
                    self.process.stdin.close()
                except OSError:
                    pass
            try:
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.process.terminate()
                try:
                    self.process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                    self.process.wait()


def control_boot_args(out):
    """Add only documented test transport kargs; never touch image branding."""
    loop = subprocess.check_output(["losetup", "--find", "--show", "--partscan", str(out / "disk.raw")], text=True).strip()
    try:
        run("udevadm", "settle")
        listing = json.loads(subprocess.check_output(["lsblk", "--json", "--fs", loop], text=True))
        esp = [row for row in listing["blockdevices"][0].get("children", []) if row.get("fstype") == "vfat"]
        if len(esp) != 1:
            raise RuntimeError("installed system did not expose one EFI System Partition")
        with tempfile.TemporaryDirectory(prefix="athens-esp-") as temporary:
            mount = Path(temporary)
            run("mount", "/dev/" + esp[0]["name"], str(mount))
            try:
                entries = list((mount / "loader/entries").glob("*.conf"))
                if not entries:
                    raise RuntimeError("installed bootloader did not provide editable BLS entries")
                changes = []
                for entry in entries:
                    original = entry.read_text()
                    if not any(line.startswith("options ") for line in original.splitlines()):
                        raise RuntimeError("installed boot entry has no kernel options")
                    updated = "\n".join(line + " systemd.wants=sshd.service console=tty0 console=ttyS0,115200n8"
                                        if line.startswith("options ") else line for line in original.splitlines()) + "\n"
                    entry.write_text(updated)
                    changes.append({"entry": str(entry.relative_to(mount)), "before_sha256": hashlib.sha256(original.encode()).hexdigest(),
                                    "after_sha256": hashlib.sha256(updated.encode()).hexdigest()})
                return {"added_kargs": ["systemd.wants=sshd.service", "console=tty0", "console=ttyS0,115200n8"],
                        "image_files_modified": False, "bls_entries": changes}
            finally:
                run("umount", str(mount))
    finally:
        run("losetup", "--detach", loop)


def type_secret(vm, secret):
    # Generated hex only: no shell interpolation, monitor transcript or recipe.
    if not re.fullmatch("[a-f0-9]+", secret):
        raise RuntimeError("secret transport accepts generated hex credentials only")
    if vm.safe:
        raise RuntimeError("refusing secret input while screenshots are enabled")
    try:
        for char in secret:
            vm.qmp("human-monitor-command", {"command-line": f"sendkey {char}"})
            time.sleep(0.03)
        vm.qmp("human-monitor-command", {"command-line": "sendkey ret"})
    except Exception:
        raise RuntimeError("secret-input transport failed; capture remains disabled") from None


def locate_artwork(engine, out):
    """Measure actual boxes using independent committed artwork, not a baseline frame."""
    import cv2
    import numpy as np
    import yaml

    spec = yaml.safe_load((out / "install-pipeline-screens.yaml").read_text())
    calibration = {}
    for checkpoint, frame, region, asset in (
            ("luks-before-secret", "luks-before-secret", "watermark", "athens-boot-logo.png"),
            ("installed-about", "installed-about", "logo", "athens-logo.svg")):
        with tempfile.TemporaryDirectory(prefix="athens-template-") as temporary:
            template = Path(temporary) / "reference.png"
            run("convert", str(engine / "branding/athens" / asset), "-background", "none",
                "-resize", "128x128", str(template))
            expected = cv2.imread(str(template), cv2.IMREAD_UNCHANGED)
            actual = cv2.imread(str(out / f"{frame}.png"), cv2.IMREAD_COLOR)
            if expected is None or actual is None:
                raise RuntimeError("actual artwork frame or independent reference cannot be decoded")
            mask = expected[:, :, 3] if expected.shape[2] == 4 else np.full(expected.shape[:2], 255, dtype=np.uint8)
            scores = cv2.matchTemplate(actual, expected[:, :, :3], cv2.TM_SQDIFF_NORMED, mask=mask)
            distance, _, position, _ = cv2.minMaxLoc(scores)
            if not np.isfinite(distance) or distance > 0.02:
                raise RuntimeError(f"canonical artwork could not be located in actual {frame} (not qualified)")
            height, width = actual.shape[:2]
            box = [position[0] / width, position[1] / height, 128 / width, 128 / height]
            for item in spec["checkpoints"]:
                if item["id"] == checkpoint:
                    for crop in item.get("regions", []):
                        if crop["id"] == region:
                            crop["box"] = box
            calibration[frame] = {"box": box, "source": f"committed-independent-{asset}", "template_distance": distance,
                                  "frame_sha256": sha(out / f"{frame}.png")}
    target = out / "measured-install-pipeline-screens.yaml"
    target.write_text(yaml.safe_dump(spec))
    (out / "region-calibration.json").write_text(json.dumps(calibration, indent=2) + "\n")
    return target


def automatic_journey(vm, args, engine, out, receipt):
    credentials = {"mode": "live", "username": "athenscheck", "fullname": "Athens Qualification",
                   "password": secrets.token_hex(12), "luks": secrets.token_hex(12), "nonce": uuid.uuid4().hex}
    code = git(ROOT, "show", f"{receipt['source']['source_commit']}:files/live/gui-driver.py").decode()
    driver = GuestDriver(args.ssh_port, credentials, code, key=args.automation_key)
    installed = None
    try:
        driver.start()
        for stage in ("live-desktop", "installer-welcome", "installer-source", "installer-disk",
                      "installer-encryption", "installer-summary", "installer-done"):
            data = driver.receive(stage, timeout=3700 if stage == "installer-done" else 180)
            if "state" in data:
                if data["state"].get("nonce") != credentials["nonce"]:
                    raise RuntimeError("native session state has the wrong run nonce")
                validate_state(data["state"], "live", receipt)
            vm.safe = True  # Driver proves no populated credential controls.
            vm.capture(stage, receipt)
            if stage == "installer-welcome":
                with (out / "walkthrough.tap").open("w") as log:
                    run(sys.executable, str(engine / "scripts/installer-walkthrough.py"), str(vm.hmp_path),
                        str(out), "18", "pantheon", "--strict", f"--spec={out / 'installer-screens.yaml'}",
                        f"--vnc={vm.vnc_path}", stdout=log, stderr=subprocess.STDOUT)
                report = json.loads((out / "walkthrough-pantheon.json").read_text())
                if report.get("ocr") is not True or report.get("failures") != 0 or any(
                        report.get("screens", {}).get(name) is not True for name in ("welcome", "disk", "encryption")):
                    raise RuntimeError("actual empty-form walkthrough or required OCR is unproven")
            vm.safe = False  # Also disables failure screenshots during all input.
            driver.acknowledge()
        driver.stop()
        vm.qmp("system_powerdown")
        vm.process.wait(timeout=120)
        vm.stop()
        receipt["disk"] = encrypted_disk(out)
        receipt["test_boot_instrumentation"] = control_boot_args(out)
        installed = VM(out, args.firmware.resolve(), out / "OVMF_VARS.fd", ssh_port=args.ssh_port)
        receipt["vms"].append(installed.start())
        with tempfile.TemporaryDirectory(prefix="athens-empty-prompt-") as temporary:
            frame = Path(temporary) / "prompt.png"
            deadline = time.monotonic() + 300
            while time.monotonic() < deadline:
                installed.qmp("screendump", {"filename": str(frame), "format": "png"})
                text = subprocess.check_output(["tesseract", str(frame), "stdout", "--psm", "11"], stderr=subprocess.DEVNULL, text=True).casefold()
                if any(word in text for word in ("kernel panic", "emergency mode")):
                    raise RuntimeError("installed boot failed before the LUKS prompt")
                if any(word in text for word in ("passphrase", "password", "unlock")):
                    break
                time.sleep(2)
            else:
                raise RuntimeError("no actual empty LUKS prompt was observed")
        installed.safe = True
        installed.capture("luks-before-secret", receipt)
        installed.safe = False
        type_secret(installed, credentials["luks"])
        credentials["mode"] = "greeter"
        driver = GuestDriver(args.ssh_port, credentials, code, greeter=True)
        driver.start()
        driver.receive("installed-greeter")
        installed.safe = True
        installed.capture("installed-greeter", receipt)
        installed.safe = False
        driver.acknowledge()
        driver.receive("submit-login")
        installed.qmp("human-monitor-command", {"command-line": "sendkey ret"})
        driver.acknowledge()
        driver.stop()
        credentials["mode"] = "session"
        credentials["nonce"] = uuid.uuid4().hex
        driver = GuestDriver(args.ssh_port, credentials, code)
        driver.start()
        data = driver.receive("installed-desktop")
        if data["state"].get("nonce") != credentials["nonce"]:
            raise RuntimeError("installed session receipt has the wrong nonce")
        validate_state(data["state"], "installed", receipt)
        # Dismiss optional onboarding using real window-manager keys, not settings.
        for _ in range(2):
            installed.qmp("human-monitor-command", {"command-line": "sendkey alt-f4"})
            time.sleep(1)
        installed.safe = True
        installed.capture("installed-desktop", receipt)
        installed.safe = False
        driver.acknowledge()
        driver.receive("installed-about")
        installed.safe = True
        installed.capture("installed-about", receipt)
        installed.safe = False
        driver.acknowledge()
        driver.stop()
        return installed
    except BaseException:
        driver.stop()
        if installed is not None:
            installed.stop()
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("media", type=Path, help="fresh normal build-live-iso output directory")
    parser.add_argument("--contract", required=True, type=Path, help=f"TunaOS checkout at {PIN}")
    parser.add_argument("--output", type=Path, default=Path("athens-luks-qualification"))
    parser.add_argument("--firmware", type=Path, default=Path("/usr/share/OVMF/OVMF_CODE_4M.fd"))
    parser.add_argument("--variables", type=Path, default=Path("/usr/share/OVMF/OVMF_VARS_4M.fd"))
    parser.add_argument("--manual", action="store_true", help="Optional operator-assisted VNC mode; default is real GTK automation")
    parser.add_argument("--automation-key", type=Path, help="Disposable private key OUTSIDE evidence, matching the qualification ISO")
    parser.add_argument("--ssh-port", type=int, default=2223, help="Loopback-only restricted guest control port")
    parser.add_argument("--control-root", type=Path, default=ROOT.parent, help="Parent of committed tromso/ and xfce-linux/ checkouts for actual wrong-city controls")
    args = parser.parse_args()
    if os.geteuid() != 0 or (args.manual and not sys.stdin.isatty()):
        parser.error("run with sudo; --manual additionally requires an interactive VNC operator")
    if not args.manual and (not args.automation_key or not args.automation_key.is_file()):
        parser.error("automatic mode requires the disposable --automation-key")
    for tool in ("qemu-system-x86_64", "qemu-img", "tesseract", "convert", "losetup", "lsblk", "udevadm", "ssh", "sshpass"):
        if not shutil.which(tool):
            parser.error(f"missing qualification dependency: {tool}")
    for path in (args.firmware, args.variables):
        if not path.is_file():
            parser.error(f"missing UEFI firmware: {path}")
    media = args.media.resolve()
    iso = media / "athens-live.iso"
    source = json.loads((media / "source.json").read_text())
    commit = git(ROOT, "rev-parse", "HEAD").decode().strip()
    if not re.fullmatch(r"[0-9a-f]{40}", source.get("source_commit", "")) or source["source_commit"] != commit:
        parser.error("ISO provenance is not the current exact source commit")
    run("git", "-C", str(ROOT), "diff", "--quiet", "HEAD", "--")
    if source.get("qualification_smoke_iso") or source.get("installer") != "org.tunaos.InstallerXfce":
        parser.error("use normal installer ISO media, not auto-poweroff smoke or installer-free old media")
    if not args.manual:
        if not source.get("qualification_ssh"):
            parser.error("automatic mode requires an ISO built with --automation-public-key")
        public_key = subprocess.check_output(["ssh-keygen", "-y", "-f", str(args.automation_key)], text=True).strip()
        public_key = " ".join(public_key.split()[:2])
        if hashlib.sha256(public_key.encode()).hexdigest() != source["automation_public_key_sha256"]:
            parser.error("automation private key does not match this ISO")
    if sha(iso) != source["iso_sha256"]:
        parser.error("ISO hash does not match its assembly receipt")
    out = args.output.resolve()
    out.mkdir()  # Never admit old frames or reuse another run's disk/evidence.
    receipt = {"schema_version": 1, "proof_class": "operator-assisted-real-gui" if args.manual else "native-atspi-real-gui", "outcome": "failed",
               "run_id": uuid.uuid4().hex, "contract_commit": PIN, "source": source,
               "frames": {}, "states": {}, "vms": [], "cleanup": False}
    vm = None
    try:
        with tempfile.TemporaryDirectory(prefix="athens-contract-") as temporary:
            engine = Path(temporary)
            stage_engine(args.contract.resolve(), engine, commit)
            artwork_controls = prepare_controls(engine, args.control_root.resolve())
            receipt["artwork_controls"] = artwork_controls
            for spec in ("install-pipeline-screens.yaml", "installer-screens.yaml"):
                (out / spec).write_bytes(git(ROOT, "show", f"{commit}:tests/{spec}"))
            run("qemu-img", "create", "-f", "raw", str(out / "disk.raw"), "64G")
            shutil.copyfile(args.variables, out / "OVMF_VARS.fd")
            vm = VM(out, args.firmware.resolve(), out / "OVMF_VARS.fd", iso, ssh_port=None if args.manual else args.ssh_port)
            receipt["vms"].append(vm.start())
            if args.manual:
                confirm("Wait for the fresh live Pantheon desktop. Set display resolution to 1920x1080 if needed.\n"
                        "Keep windows closed; do not change the wallpaper or theme.")
                defaults_state(vm, "live", receipt)
                vm.capture("live-desktop", receipt)
                confirm("Launch 'Install TunaOS Athens' from Applications. Leave the welcome page visible.\n"
                        "Do not enter any password/passphrase yet. No other screen recorder may be running.")
                vm.capture("installer-welcome", receipt)
                # Only EMPTY forms are visited by this upstream keyboard walkthrough.
                with (out / "walkthrough.tap").open("w") as log:
                    run(sys.executable, str(engine / "scripts/installer-walkthrough.py"), str(vm.hmp_path),
                        str(out), "18", "pantheon", "--strict", f"--spec={out / 'installer-screens.yaml'}",
                        f"--vnc={vm.vnc_path}", stdout=log, stderr=subprocess.STDOUT)
                walkthrough = json.loads((out / "walkthrough-pantheon.json").read_text())
                if walkthrough.get("ocr") is not True or walkthrough.get("failures") != 0 or any(
                        walkthrough.get("screens", {}).get(screen) is not True for screen in ("welcome", "disk", "encryption")):
                    raise RuntimeError("required real GUI walkthrough pages or OCR are unproven")
                confirm("Using Back if needed, show Disk encryption. Select Passphrase, but leave both fields EMPTY.\n"
                        "The target disk must be the disposable 64G /dev/vda, and source must be the embedded Athens image.")
                vm.capture("installer-encryption", receipt)
                vm.safe = False
                confirm("CAPTURES ARE NOW DISABLED. Complete passphrase and account fields directly in VNC.\n"
                        "Use a new account that has never set a wallpaper. Continue to Confirm installation.\n"
                        "Ensure NO password, passphrase, recovery key, or populated credential form is visible.", "SAFE-SUMMARY")
                vm.safe = True
                vm.capture("installer-summary", receipt)
                vm.safe = False
                confirm("Click Install Now in the actual shipped GUI. Wait for successful completion.\n"
                        "Do not run fisherman/bootc yourself. No credential/recovery-key view may remain visible.", "SAFE-DONE")
                vm.safe = True
                vm.capture("installer-done", receipt)
                confirm("Use the live desktop's Shut Down action. Wait until the VM has fully powered off.", "POWERED-OFF")
                if vm.process.poll() is None:
                    raise RuntimeError("live VM has not powered off; refusing an unsafe disk inspection")
                vm.stop()
                receipt["disk"] = encrypted_disk(out)
                vm = VM(out, args.firmware.resolve(), out / "OVMF_VARS.fd")
                receipt["vms"].append(vm.start())
                confirm("Cold boot now has NO ISO and NO network. Wait for the branded LUKS prompt.\n"
                        "Do NOT type the passphrase yet; its input field must be EMPTY.", "EMPTY-LUKS-PROMPT")
                vm.safe = True
                vm.capture("luks-before-secret", receipt)
                vm.safe = False
                confirm("CAPTURES ARE DISABLED. Enter the LUKS passphrase directly in VNC.\n"
                        "Wait for LightDM, with its password field EMPTY. Do not log in yet.", "SAFE-GREETER")
                vm.safe = True
                vm.capture("installed-greeter", receipt)
                vm.safe = False
                confirm("CAPTURES ARE DISABLED. Log into the fresh installed user directly in VNC.\n"
                        "Close onboarding and leave the normal desktop visible. Do not set wallpaper or theme.", "SAFE-DESKTOP")
                defaults_state(vm, "installed", receipt)
                vm.capture("installed-desktop", receipt)
                confirm("Open System Settings → System/About. Show the actual Athens OS name and logo.\n"
                        "No terminal, authentication dialog or secret may be visible.", "SAFE-ABOUT")
                vm.capture("installed-about", receipt)
            else:
                vm = automatic_journey(vm, args, engine, out, receipt)
            # Bind every required frame to this owned run before judging pixels.
            for name, frame in receipt["frames"].items():
                if sha(out / f"{name}.png") != frame["sha256"]:
                    raise RuntimeError("a captured frame changed before admission")
            measured_spec = locate_artwork(engine, out)
            judge(engine, out, measured_spec, "install-checkpoints-pantheon")
            receipt["negative_controls"] = negative_controls(
                engine, out, measured_spec, receipt["frames"], artwork_controls)
            receipt["outcome"] = "passed"
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError, EOFError, KeyboardInterrupt) as error:
        # Never take a diagnostic screenshot: the failure may be credential entry.
        receipt["failure"] = str(error)
        raise
    finally:
        if vm is not None:
            vm.stop()
        receipt["cleanup"] = vm is None or vm.process is None or vm.process.poll() is not None
        (out / "journey.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(f"Qualified real GUI/LUKS branding evidence: {out}")


if __name__ == "__main__":
    main()
