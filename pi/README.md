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

The code assumes by default that your Redis server is running on `localhost` port `6379`.  If this is not the case, you'll need to set the `REDIS_URL` environment variable to a valid Redis URL describing where and how to connect to your Redis server.

For example, here's how to connect to a server on `myhost` at port `9999` with password `secret123`:

```
export REDIS_URL=redis://default:secret123@myhost:9999/
```

If you have a username and a password for your Redis server, use something like this:

```
export REDIS_URL=redis://myusername:secret123@myhost:9999/
```

If you don't need a username or a password:

```
export REDIS_URL=redis://myhost:9999/
```

Be sure to configure both the capture script and the separate server component to talk to the same Redis instance!

### Running the Capture Script

TODO