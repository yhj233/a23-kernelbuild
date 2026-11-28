#!/usr/bin/env python3
"""Add the BMA222E accelerometer node to U-Boot's Q8 tablet device tree.

Why U-Boot and not the kernel tree: on this board the kernel boots with the
DTB produced by the U-Boot build (it carries the simple-framebuffer set up by
U-Boot), the mainline kernel dts is never used.  So the i2c child node has to
exist in U-Boot's own dts for the kernel to probe the chip.

Verified on the device with i2c-tools:
    i2cdetect -y -r 1        -> 0x19 present
    i2cget   -y 1 0x19 0x00  -> 0xf8  (BMA222E chip id)
    data regs 0x02..0x07     -> 12-bit left aligned, Z = 0xC101 >> 4 = -1008
                                -> -0.98 g flat on the desk, so the part is
                                alive and only lacks a driver binding.

i2c1 is already enabled (status = "okay") by sunxi-reference-design-tablet.dtsi,
which is included by sun8i-a23-q8-tablet.dts, so only the child node is needed.
"""

import os
import sys

NODE = """
/*
 * Bosch BMA222E accelerometer (chip id 0xF8) on i2c1 address 0x19.
 * No interrupt line is wired on this board, the driver polls.
 */
&i2c1 {
	accelerometer@19 {
		compatible = "bosch,bma222e";
		reg = <0x19>;
	};
};
"""

DEFAULT = 'arch/arm/dts/sun8i-a23-q8-tablet.dts'


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT
    if not os.path.exists(path):
        sys.exit('missing dts: ' + path)
    text = open(path).read()
    if 'bma222e' in text:
        print('already patched:', path)
        return
    if not text.endswith('\n'):
        text += '\n'
    open(path, 'w').write(text + NODE)
    print('patched', path, '(+%d bytes)' % len(NODE))
    print('--- tail ---')
    print('\n'.join(open(path).read().splitlines()[-12:]))


if __name__ == '__main__':
    main()
