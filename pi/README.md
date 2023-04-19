# TODO capture README

![Raspberry Pi 3 with Camera Module attached](../raspberry_pi_3_with_camera_module.jpg)

## Overview

TODO

## How it Works

TODO

## Setup

TODO intro

### Camera Setup 

Raspberry Pi 3B with Camera Module v2.1 and Raspberry Pi OS Bullseye

TODO info...

Ensure the following are in `/boot/config.txt` and reboot the Raspberry Pi after making any changes.

```
camera_auto_detect=0
dtoverlay=vc4-kms-v3d
max_framebuffers=10
dtoverlay=imx219
```

The `imx219` value may differ for your camera.  I was using the Raspberry Pi Camera Module v2.1.

### Environment Variables

TODO

### Running the Capture Script

TODO