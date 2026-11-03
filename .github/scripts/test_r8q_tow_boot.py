import importlib.util
from pathlib import Path
import struct
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

    def boot_image(self, binary):
        header = bytearray(4096)
        header[:8] = b"ANDROID!"
        struct.pack_into("<I", header, 8, len(binary))
        struct.pack_into("<II", header, 36, 4096, 2)
        return bytes(header) + binary

    def test_packaged_tow_boot(self):
        check_r8q.verify_boot_image(self.binary, self.boot_image(self.binary))

    def test_packaged_plain_u_boot(self):
        with self.assertRaises(ValueError):
            check_r8q.verify_boot_image(self.binary, self.boot_image(b"U-Boot 2026.10\0"))

    def test_markers_outside_kernel_do_not_pass(self):
        image = self.boot_image(b"U-Boot 2026.10\0") + self.binary
        with self.assertRaises(ValueError):
            check_r8q.verify_boot_image(self.binary, image)

    def test_same_size_wrong_payload(self):
        with self.assertRaises(ValueError):
            check_r8q.verify_boot_image(
                self.binary, self.boot_image(self.binary.replace(b"Tow-Boot", b"U-Boot  "))
            )

    def test_truncated_boot_image(self):
        image = self.boot_image(self.binary)
        for size in (0, 7, 100, 1659, 4096, len(image) - 1):
            with self.subTest(size=size), self.assertRaises(ValueError):
                check_r8q.verify_boot_image(self.binary, image[:size])

    def test_invalid_boot_image_header(self):
        for offset, value in ((0, 0), (8, 0), (36, 2048), (40, 3)):
            image = bytearray(self.boot_image(self.binary))
            struct.pack_into("<I", image, offset, value)
            with self.subTest(offset=offset), self.assertRaises(ValueError):
                check_r8q.verify_boot_image(self.binary, image)
