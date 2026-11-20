setenv bootargs console=tty0 console=ttyS0,115200 root=/dev/mmcblk0p2 rootwait panic=10 fbcon=rotate:0
load mmc 0:1 0x43000000 sun8i-a23-q8-tablet.dtb
load mmc 0:1 0x42000000 zImage
bootz 0x42000000 - 0x43000000
