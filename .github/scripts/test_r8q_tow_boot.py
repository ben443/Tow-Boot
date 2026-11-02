import importlib.util
from pathlib import Path
import unittest


spec = importlib.util.spec_from_file_location(
    "check_r8q", Path(__file__).with_name("check-r8q-tow-boot.py")
)
check_r8q = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_r8q)


class TowBootVerificationTests(unittest.TestCase):
    config = """
CONFIG_TOW_BOOT_MENU=y
CONFIG_PDCURSES=y
CONFIG_PDCURSES_PREFER_VIDCONSOLE=y
CONFIG_VIDEO_LOGO=y
CONFIG_SPLASH_SCREEN=y
CONFIG_BOOTSTD=y
CONFIG_BUTTON_REMAP_PHONE_KEYS=y
CONFIG_ENV_IS_NOWHERE=y
CONFIG_OF_SEPARATE=y
CONFIG_DEFAULT_DEVICE_TREE="qcom/sm8250-samsung-r8q"
"""
    binary = b"\0".join((
        b"Tow-Boot 2026.10",
        b"Tow-Boot curses-based menu interface.",
        b"board_identifier=samsung-galaxyS20FER8q",
        b"menucmd=setenv bootcmd run menucmd; run towboot_menu",
        b"towboot_menu=tb_menu new;",
        b"bootcmd=bootefi bootmgr; pause; run menucmd",
        b"button_cmd_0=run menucmd",
        b"",
    ))

    def test_tow_boot(self):
        check_r8q.verify(self.config, self.binary)

    def test_each_required_setting(self):
        for setting in self.config.strip().splitlines():
            with self.subTest(setting=setting), self.assertRaises(ValueError):
                check_r8q.verify(self.config.replace(setting, ""), self.binary)

    def test_each_required_binary_marker(self):
        for marker in self.binary.split(b"\0")[:-1]:
            with self.subTest(marker=marker), self.assertRaises(ValueError):
                check_r8q.verify(self.config, self.binary.replace(marker, b""))

    def test_wrong_device_tree(self):
        with self.assertRaises(ValueError):
            check_r8q.verify(self.config.replace("samsung-r8q", "other"), self.binary)

    def test_branding_alone_is_not_tow_boot(self):
        with self.assertRaises(ValueError):
            check_r8q.verify(self.config, b"Tow-Boot 2026.10\0")
