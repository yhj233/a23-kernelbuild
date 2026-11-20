# A23 平板主线内核编译 (PLOYER momo9 / Inet D70, Allwinner A23)

用 GitHub Actions 交叉编译 Linux 6.1 主线内核，给 A23 (sun8i) 平板使用。

## 目标

- **framebuffer console**：`CONFIG_FB` + `CONFIG_FB_SIMPLE` + `CONFIG_FRAMEBUFFER_CONSOLE`
  → 开机屏幕直接出 Linux console（解决"内核起来了但纯黑屏"）
- **Mali-400MP2 GPU**：`CONFIG_DRM_LIMA=y` 开源驱动（OpenGL ES 2.0 / EGL）
  → 视频、老版 Minecraft 的图形基础
- **USB dual-role**：`CONFIG_USB_MUSB_DUAL_ROLE=y`

配置文件 `kernel.config` 来自 VictorIstratii151/linux_tablet 的
`console_usb_working_kernel_config`（作者调好的 6.1.0-rc8 配置）。

## 触发编译

push 到 `main` 或在 Actions 页手动点 "Run workflow"。编译产物在 Artifacts：

- `zImage` — 内核
- `sun8i-a23-q8-tablet.dtb` — 设备树
- `boot.scr` — U-Boot 启动脚本
- `kernel-final.config` — olddefconfig 补齐后的最终配置

## 部署到 SD 卡 p1 (FAT)

```
zImage                     -> /boot 或 p1 根
sun8i-a23-q8-tablet.dtb    -> p1 根
boot.scr                   -> p1 根
```

boot.scr 里 bootargs 用 `console=tty0 console=ttyS0,115200`，
root 在 `/dev/mmcblk0p2`。

## 备注

- A23 BootROM 是 NAND 优先，SD 卡不会自动引导。用 `adb shell reboot efex`
  进 FEL，然后 `sunxi-fel uboot u-boot-sunxi-with-spl.bin` 内存加载引导。
- 若屏幕仍黑：主线 dtb 的 simple-framebuffer 可能与实际 panel 时序不符，
  需换 U-Boot 仓库生成的 dtb（作者 README 的做法），或调 dts 的 display 节点。
