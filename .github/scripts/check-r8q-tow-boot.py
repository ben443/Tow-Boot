#!/usr/bin/env python3

import argparse
from pathlib import Path
import re
import struct


def verify(config, binary):
    required = {
        "CONFIG_TOW_BOOT_MENU": "y",
        "CONFIG_PDCURSES": "y",
        "CONFIG_PDCURSES_PREFER_VIDCONSOLE": "y",
        "CONFIG_VIDEO_LOGO": "y",
        "CONFIG_SPLASH_SCREEN": "y",
        "CONFIG_BOOTSTD": "y",
        "CONFIG_BUTTON_REMAP_PHONE_KEYS": "y",
        "CONFIG_ENV_IS_NOWHERE": "y",
        "CONFIG_OF_SEPARATE": "y",
        "CONFIG_DEFAULT_DEVICE_TREE": '"qcom/sm8250-samsung-r8q"',
    }
    settings = dict(
        line.split("=", 1)
        for line in config.splitlines()
        if line.startswith("CONFIG_") and "=" in line
    )
    for key, value in required.items():
        if settings.get(key) != value:
            raise ValueError(f"expected {key}={value}, got {settings.get(key)!r}")

    if not re.search(rb"Tow-Boot \d{4}\.\d{2}", binary):
        raise ValueError("firmware is missing the Tow-Boot version banner")

    for marker in (
        b"Tow-Boot curses-based menu interface.",
        b"board_identifier=samsung-galaxyS20FER8q\0",
        b"menucmd=setenv bootcmd run menucmd; run towboot_menu\0",
        b"towboot_menu=tb_menu new;",
        b"bootcmd=bootefi bootmgr; pause; run menucmd\0",
        b"button_cmd_0=run menucmd\0",
    ):
        if marker not in binary:
            raise ValueError(f"firmware is missing {marker!r}")


def verify_boot_image(binary, image):
    if len(image) < 1660 or image[:8] != b"ANDROID!":
        raise ValueError("boot image is missing a complete Android v2 header")

    kernel_size = struct.unpack_from("<I", image, 8)[0]
    page_size, header_version = struct.unpack_from("<II", image, 36)
    if header_version != 2 or page_size != 4096:
        raise ValueError("expected Android boot image header v2 with 4096-byte pages")
    if kernel_size != len(binary) or image[page_size:page_size + kernel_size] != binary:
        raise ValueError("boot image kernel does not match the verified Tow-Boot binary")


def main():
    parser = argparse.ArgumentParser(description="Reject R8Q builds without Tow-Boot features")
    parser.add_argument("config", type=Path)
    parser.add_argument("binary", type=Path)
    parser.add_argument("--boot-image", type=Path)
    args = parser.parse_args()
    try:
        binary = args.binary.read_bytes()
        verify(args.config.read_text(), binary)
        if args.boot_image:
            verify_boot_image(binary, args.boot_image.read_bytes())
    except ValueError as error:
        parser.exit(1, f"ERROR: {error}\n")
    print("R8Q Tow-Boot menu, identity, logo configuration and phone boot path verified.")


if __name__ == "__main__":
    main()
