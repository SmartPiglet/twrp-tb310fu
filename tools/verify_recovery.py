#!/usr/bin/env python3
"""Verify a built recovery.img is a sane, TWRP-containing boot image for TB310FU."""
import struct, sys, os, gzip, lzma, subprocess, tempfile, shutil

EXPECT = {"base": 0x40078000, "ramdisk_off": 0x07c08000, "tags_off": 0x0bc08000,
          "kernel_addr": 0x40080000, "ramdisk_addr": 0x47c80000, "tags_addr": 0x4bc80000,
          "dtb_addr": 0x4bc80000, "pagesize": 2048, "header_version": 2}

def fail(msg):
    print("FAIL:", msg); sys.exit(1)

def decompress(blob, tmp):
    if blob[:2] == b"\x1f\x8b": return gzip.decompress(blob)
    if blob[:6] == b"\xfd7zXZ\x00": return lzma.decompress(blob)
    if blob[:4] == b"\x28\xb5\x2f\xfd":
        p = os.path.join(tmp, "r.zst"); open(p, "wb").write(blob)
        o = os.path.join(tmp, "r.out")
        subprocess.run(["zstd", "-d", "-f", p, "-o", o], check=True)
        return open(o, "rb").read()
    if blob[:4] == b"\x02\x21\x4c\x18":
        p = os.path.join(tmp, "r.lz4"); open(p, "wb").write(blob)
        o = os.path.join(tmp, "r.out")
        for exe in (["lz4", "-d", "-f", p, o], ["unlz4", p, o]):
            try:
                subprocess.run(exe, check=True, capture_output=True); return open(o, "rb").read()
            except Exception: pass
        fail("lz4 ramdisk but no lz4 tool")
    return blob  # assume raw cpio

def main(path):
    d = open(path, "rb").read()
    print("image size:", len(d))
    if d[:8] != b"ANDROID!":
        fail("missing ANDROID! magic (not a boot image)")
    (ksize, kaddr, rsize, raddr, ssize, saddr, tags, ps, hver, osver) = struct.unpack_from("<IIIIIIIIII", d, 8)
    print(f"header_version={hver} kernel_size={ksize} kernel_addr={kaddr:#x}")
    print(f"ramdisk_size={rsize} ramdisk_addr={raddr:#x} tags_addr={tags:#x} page_size={ps}")
    if hver < 2: fail(f"expected header v2, got v{hver}")

    koff = ps
    roff = (koff + ksize + ps - 1) // ps * ps
    doff = (roff + rsize + ps - 1) // ps * ps
    dtb_size, = struct.unpack_from("<I", d, 1648)
    dtb_addr, = struct.unpack_from("<Q", d, 1652)
    print(f"dtb_size={dtb_size} dtb_addr={dtb_addr:#x}")

    checks = {
        "kernel_addr == 0x40080000": (kaddr, EXPECT["kernel_addr"]),
        "ramdisk_addr == 0x47c80000": (raddr, EXPECT["ramdisk_addr"]),
        "tags_addr == 0x4bc80000": (tags, EXPECT["tags_addr"]),
        "page_size == 2048": (ps, EXPECT["pagesize"]),
        "dtb present": (dtb_size > 0, True),
    }
    for name, (got, want) in checks.items():
        print(("  ok   " if got == want else "  BAD  ") + f"{name} (got {got:#x})" if isinstance(got, int) else ("  ok   " if got == want else "  BAD  ") + name)
        if got != want: fail(name)

    ram = d[roff:roff + rsize]
    tmp = tempfile.mkdtemp()
    try:
        root = os.path.join(tmp, "root"); os.makedirs(root)
        cpio = decompress(ram, tmp)
        print("ramdisk uncompressed:", len(cpio), "bytes")
        p = os.path.join(tmp, "ramdisk.cpio"); open(p, "wb").write(cpio)
        r = subprocess.run(["cpio", "-idm", "--quiet", "--no-absolute-filenames"],
                           cwd=root, stdin=open(p, "rb"), capture_output=True)
        if r.returncode != 0: fail("cpio extraction failed: " + r.stderr.decode()[:400])

        entries = sum(len(f) for _, _, f in os.walk(root))
        print("ramdisk extracted files:", entries)
        twres = os.path.isdir(os.path.join(root, "twres"))
        print("  twres/ present:", twres)
        print("  twrp.fstab present:", os.path.exists(os.path.join(root, "etc", "twrp.fstab")))

        rec = os.path.join(root, "system", "bin", "recovery")
        if not os.path.exists(rec): fail("no system/bin/recovery in ramdisk")
        blob = open(rec, "rb").read()
        has_twrp = b"TWRP" in blob or b"twrp" in blob
        print(f"  recovery binary: {len(blob)} bytes, TWRP markers: {has_twrp}")
        for marker in (b"TWRP", b"twrp"):
            if marker in blob:
                i = blob.find(marker)
                print("   sample:", blob[max(0,i-40):i+40].decode("latin1", "replace").replace("\n", " "))
                break
        if not (twres or has_twrp):
            fail("no TWRP signature found - image is NOT TWRP")
        print("\nRESULT: OK - looks like a valid TWRP recovery-as-boot image for TB310FU")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

main(sys.argv[1])
