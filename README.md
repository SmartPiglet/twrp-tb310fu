# TWRP device tree + CI for Lenovo Tab M9 (TB310FU / `t6100a_wifi`)

Builds a **TWRP recovery-as-boot** image for the Lenovo Tab M9 WiFi (`TB310FU`),
via GitHub Actions using the TWRP 12.1 minimal manifest.

## Why this tree

Verified against the device's live `boot_a` partition:

| Item | Device `boot_a` | This tree | Match |
| :--- | :--- | :--- | :--- |
| DTB sha256 | `846c782b…` | `846c782b…` | exact |
| Kernel (gunzipped) sha256 | `5128c079…` | `5128c079…` | exact |
| `kernel_addr` | `0x40080000` (base `0x40078000`) | `0x40078000` | exact |
| `ramdisk_addr` | `0x47c80000` | `+0x07c08000` | exact |
| `tags_addr` | `0x4bc80000` | `+0x0bc08000` | exact |
| header version | 2 | 2 | exact |

Device has **no recovery partition** — recovery lives in `boot`
(`BOARD_USES_RECOVERY_AS_BOOT := true`).

## Build

Triggers on push to `main` or manually via **Actions → Run workflow**.
Output: `recovery.img` artifact, verified by `tools/verify_recovery.py`
(refuses to pass an image with no TWRP signature).

## Upstream

Device tree derived from `killzsh/twrp_tb310fu`
(same payload as the XDA attachment `twrp_tb310fu-main.zip`).
Kernel/DTB of this tree == the running device's stock kernel/DTB.
