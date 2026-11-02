#!/usr/bin/env python3

import argparse
from pathlib import Path
import re


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


def main():
    parser = argparse.ArgumentParser(description="Reject R8Q builds without Tow-Boot features")
    parser.add_argument("config", type=Path)
    parser.add_argument("binary", type=Path)
    args = parser.parse_args()
    try:
        verify(args.config.read_text(), args.binary.read_bytes())
    except ValueError as error:
        parser.exit(1, f"ERROR: {error}\n")
    print("R8Q Tow-Boot menu, identity, logo configuration and phone boot path verified.")


if __name__ == "__main__":
    main()
