#!/usr/bin/env python3
"""Patch U-Boot's default CONFIG_BOOTCOMMAND to boot A23 tablet from SD card p1.
   No keyboard available (USB Type-C mod killed power), so boot must be fully automatic.
"""
p = 'include/config_distro_bootcmd.h'
s = open(p).read()
old = '#ifndef CONFIG_BOOTCOMMAND\n#define CONFIG_BOOTCOMMAND "run distro_bootcmd"\n#endif'

# Try mmc 0:1 / 0:2 / 1:1 / 1:2 until zImage+dtb are found, then bootz.
# init=/bin/bash drops straight into root shell (rootfs root password is locked).
bootcmd = (
    'setenv bootargs console=tty0 console=ttyS0,115200 '
    'root=/dev/mmcblk0p2 rootwait panic=10 fbcon=rotate:0 init=/bin/bash; '
    'for dev in 0 1; do '
    'for part in 1 2; do '
    'if load mmc ${dev}:${part} 0x42000000 zImage; then '
    'if load mmc ${dev}:${part} 0x43000000 sun8i-a23-q8-tablet.dtb; then '
    'bootz 0x42000000 - 0x43000000; '
    'fi; fi; done; done'
)
new = '#undef CONFIG_BOOTCOMMAND\n#define CONFIG_BOOTCOMMAND "' + bootcmd + '"'
assert old in s, 'pattern not found!'
open(p, 'w').write(s.replace(old, new))
print('patched CONFIG_BOOTCOMMAND:')
print(bootcmd)
