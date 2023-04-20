# Image Capture Component for Raspberry Pi with Camera Module

![Raspberry Pi 3 with Camera Module attached](../raspberry_pi_3_with_camera_module.jpg)

## Overview

TODO

## How it Works

TODO

## Setup

To get this component working, you'll need to connect your camera to the Raspberry Pi, ensure the operating system is configured correctly for it and install some Python dependencies.

### Camera Setup 

TODO

Raspberry Pi 3B with Camera Module v2.1 and Raspberry Pi OS Bullseye

TODO info...

Ensure the following are in `/boot/config.txt` and reboot the Raspberry Pi after making any changes.

```
camera_auto_detect=0
dtoverlay=vc4-kms-v3d
max_framebuffers=10
dtoverlay=imx219
```

The `imx219` value may differ for your camera.  I was using the Raspberry Pi Camera Module v2.1.  If you are using something different, you'll need to research appropriate values for your camera.

### Python Setup

You need Python 3.7 or higher (I've tested this with Python 3.9.2.  To check your Python version:

```
python3 --version
```

If you need to upgrade your Python version, use your operating system's package manager or refer to [this guide from raspberrypitips.com](https://raspberrytips.com/install-latest-python-raspberry-pi/).

You'll also need the Pip package manager.  Install with:

```
sudo apt install python3-pip
```

Verify that Pip was installed correctly:

```
pip --version
```

Once you have these, use Pip to install the project requirements like so:

```
pip install -r requirements.txt
```

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

With the setup steps completed, start the capture script as follows:

```
python3 capture.py
```

You should expect to see output similar to the following on startup:

```
[0:34:17.749739445] [847]  INFO Camera camera_manager.cpp:299 libcamera v0.0.4+22-923f5d70
[0:34:17.795151761] [848]  WARN RPI raspberrypi.cpp:1357 Mismatch between Unicam and CamHelper for embedded data usage!
[0:34:17.796473001] [848]  INFO RPI raspberrypi.cpp:1476 Registered camera /base/soc/i2c0mux/i2c@1/imx219@10 to Unicam device /dev/media3 and ISP device /dev/media0
[0:34:17.814204535] [847]  INFO Camera camera.cpp:1028 configuring streams: (0) 3280x2464-BGR888
[0:34:17.814804062] [848]  INFO RPI raspberrypi.cpp:851 Sensor: /base/soc/i2c0mux/i2c@1/imx219@10 - Selected sensor format: 3280x2464-SBGGR10_1X10 - Selected unicam format: 3280x2464-pBAA
```

Your output may differ if you are using a different camera.  It appears that this warning can be ignored:

```
WARN RPI raspberrypi.cpp:1357 Mismatch between Unicam and CamHelper for embedded data usage!
```

Every 10 seconds or so, the script will capture a new image. Expect to see output similar to the following:

```
Stored new image at image:1681923128
{'SensorTimestamp': 2058296354000, 'ScalerCrop': (0, 0, 3280, 2464), 'DigitalGain': 1.1096521615982056, 'ColourGains': (1.1879777908325195, 2.4338300228118896), 'SensorBlackLevels': (4096, 4096, 4096, 4096), 'AeLocked': False, 'Lux': 85.72087097167969, 'FrameDuration': 59489, 'ColourCorrectionMatrix': (1.6235777139663696, -0.38433241844177246, -0.23924528062343597, -0.5687134861946106, 2.019625425338745, -0.45091837644577026, -0.09334515780210495, -1.2399080991744995, 2.3332533836364746), 'AnalogueGain': 4.0, 'ColourTemperature': 2874, 'ExposureTime': 59413}
```

The camera metadata isn't stored in Redis, it's just output for informational purposes.  If any of it is considered useful enough to keep, it should be easy to modify `capture.py` to add it to the Redis Hash that stores the image and associated data.

To stop the script, press Ctrl-C.