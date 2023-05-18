# Image Capture Component for Raspberry Pi with Camera Module

![Raspberry Pi 3 with Camera Module attached](../raspberry_pi_3_with_camera_module.jpg)

## Overview

This folder contains the Python code for the image capture component of this project.  It runs on a Raspberry Pi with a Raspberry Pi Camera Module attached.

Every so many seconds (configurable), the code takes a new picture in JPEG format and stores it in a Redis Hash along with some basic metadata.  The key name for each hash is `image:<unix time stamp when image was captured>`.

I've tested this on a [Raspberry Pi 3B](https://www.raspberrypi.com/products/raspberry-pi-3-model-b/) using both the [Raspberry Pi Camera Module v2.1](https://www.raspberrypi.com/products/camera-module-v2/) and [Raspberry Pi Camera Module v3](https://www.raspberrypi.com/products/camera-module-3/).  Other models of Raspberry Pi that have the camera connector ([3A+](https://www.raspberrypi.com/products/raspberry-pi-3-model-a-plus/), [3B+](https://www.raspberrypi.com/products/raspberry-pi-3-model-b-plus/), [4B](https://www.raspberrypi.com/products/raspberry-pi-4-model-b/) etc) should work too.

I haven't tested with the [High Quality Camera](https://www.raspberrypi.com/products/raspberry-pi-high-quality-camera/).  Of the cheaper models, the v3 is a good choice for this project as it has auto focus and higher resolution than the v2.1 and is easy to find online at a reasonable price.  The pictures from my v2.1 camera can be blurry as there's no auto focus.

**Note:** As Redis keeps a copy of all the data in memory, you should bear in mind that an 8Mb image file will require at least 8Mb of RAM on the Redis server.  To help manage the amount of memory used, this project automatically expires the image data from Redis after a configurable amount of time (see later for details).

## How it Works

All of the code for this component is in a single file: `capture.py`.  Here's a high level run through of how it works...  You should also refer to the redis-py documentation and [Raspberry Pi's Picamera2 library documentation](https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf).

The first thing that the script does is initialize and configure the `Picamera2` library:

```python
picam2 = Picamera2()
picam2.start_preview(Preview.NULL)
camera_config = picam2.still_configuration
picam2.configure(camera_config)
...
picam2.start()
```

The v3 camera module has autofocus capabilities.  These are enabled like so, and only if an environment variable is set to do so (see later for details):

```python
if CAMERA_AUTOFOCUS == True:
    picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})
```

Use the `Picamera2` documentation to adjust the camera configuration in `camera_config` e.g. to capture lower resolution pictures.  This configuration assumes we are running on a headless Raspberry Pi so there's no preview window required.

Next, a connection to Redis is established, using the value of an environment variable:

```python
redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
```

The code then enters an infinite loop, in which is captures an image plus some metadata from the camera, stores it in Redis and sleeps for a configurable number of seconds before doing it all again.

If the camera module has autofocus and it is enabled... we start an autofocus cycle to make sure that the camera's focus is in the right place:

```python
if CAMERA_AUTOFOCUS == True:
    picam2.autofocus_cycle()
```

This is synchronous, so may take a short amount of time to complete.

We want to capture the image into a file like structure in memory, rather than write it to the filesystem.  We use an [in memory binary stream](https://docs.python.org/3/library/io.html#binary-i-o) declared like this:

```python
image_data = io.BytesIO()
```

An image from the camera is grabbed into that binary stream buffer, and we work out the current UNIX timestamp (seconds since 1 January 1970):

```python
image_metadata = picam2.capture_file(image_data, format="jpeg")
current_timestamp = int(time.time())
```

The return value of `picam2.capture_file` is some metadata from the camera.  This isn't currently stored in Redis, but is printed out so you can determine if any of it is useful to you.  See later in this file for an example.

Now it's time to create a Hash in Redis and store our image plus a couple of other pieces of data there, including the Lux value from the metadata:

```python
redis_key = f"image:{current_timestamp}"
data_to_save = dict()
data_to_save["image_data"] = image_data.getvalue()
data_to_save["timestamp"] = current_timestamp
data_to_save["mime_type"] = "image/jpeg"
data_to_save["lux"] = int(image_metadata["Lux"])
```

First, we create the key name we're going to use when storing the Hash.  It's `image:<timestamp>`.

`data_to_save` is a Python dictionary containing the name/value pairs to store in the Redis Hash. This needs to be a flat map of name/value pairs - nested structure isn't allowed in a Redis Hash.  If you want more complex data structure, use the [Redis JSON data type](https://redis.io/docs/stack/json/) in Redis Stack.

Hashes in Redis are schemaless, so if you add extra fields there's no need to change any database schema (if you're looking for one, it doesn't exist!).  You'll just need to modify any application code that reads the Hashes to use new fields.

We store the bytes of the image, the timestamp and the MIME or media type of the image... so that any front end knows what encoding the data in `image_data` is in.

Saving the Hash to Redis is then simply a matter of running the [`HSET` command](https://redis.io/commands/hset/), passing it the key name and dict of name/value pairs to store:

```python
redis_client.hset(redis_key, mapping = data_to_save)
```

As it stands, the images will stay in Redis until manually deleted.  If you want to set a time to live on the image, use the [EXPIRE command](https://redis.io/commands/expire/).  Redis will consider the Hash deleted after the number of seconds you specify has passed, freeing up resources associated with it on the Redis server.  To implement this with a 1hr expiry time, modify the code as follows:

```python
redis_client.hset(redis_key, mapping = data_to_save)
redis_client.expire(redis_key, 3600) # 60 secs = 1 min x 60 = 1hr
```

Redis also has an [EXPIREAT command](https://redis.io/commands/expireat/) if you prefer to specify a time and date for expiry, rather than a number of seconds in the future.

TODO update the above for pipelining and expiry.

## Setup

To get this component working, you'll need to connect your camera to the Raspberry Pi, ensure the operating system is configured correctly for it and install some Python dependencies (to connect to Redis).

These instructions assume you are running the latest version of Raspberry Pi OS.  They have been tested with the following version:

```
$ cat /etc/os-release
PRETTY_NAME="Raspbian GNU/Linux 11 (bullseye)"
NAME="Raspbian GNU/Linux"
VERSION_ID="11"
VERSION="11 (bullseye)"
VERSION_CODENAME=bullseye
ID=raspbian
ID_LIKE=debian

$ uname -s -r -v -m
Linux 6.1.21-v7+ #1642 SMP Mon Apr  3 17:20:52 BST 2023 armv7l
```

### Camera Setup 

Setting up the camera may require some changes to the operating system configuration of the Raspberry Pi.  This is what worked for me on the Raspberry Pi 3B using either the Camera Module v2.1 or v3 (recommended).  

First, connect the camera to the Raspberry Pi with the ribbon cable provided. If you are unsure how to do this, follow Raspberry Pi's [instructions here](https://projects.raspberrypi.org/en/projects/getting-started-with-picamera/2).

Then, as the root user (`sudo vi /boot/config.txt`), ensure the following are in `/boot/config.txt` and add them if not:

```
camera_auto_detect=0
dtoverlay=vc4-kms-v3d
max_framebuffers=10
dtoverlay=imx219
```

The `imx219` value may differ for your camera.  Use `imx219` for the Raspberry Pi Camera Module v2.1, or `imx708` for the v3.  If you are using something different, you'll need to research appropriate values for your camera.  Raspberry Pi provide this information in their [camera documentation](https://www.raspberrypi.com/documentation/accessories/camera.html#preparing-the-software).

If you made any changes, save them and **reboot the Raspberry Pi** (`sudo reboot`).

### Python Setup

You need Python 3.7 or higher (I've tested this with Python 3.9.2).  To check your Python version:

```
python3 --version
```

The operating system should have been supplied with an appropriate Python version pre-installed.  If you find that you need to upgrade your Python version, use your operating system's package manager or refer to [this guide from raspberrypitips.com](https://raspberrytips.com/install-latest-python-raspberry-pi/).

You'll also need the Pip package manager.  Install it with:

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

You'll also need to set the following environment variables:

* `IMAGE_CAPTURE_FREQUENCY` - set this to the number of seconds that you want the code to wait between capturing images, e.g. `30`.
* `IMAGE_EXPIRY` - set this to the number of seconds that you want the image data to be stored in Redis for before it is expired e.g. `300` for 5 minutes.
* `CAMERA_AUTOFOCUS` - set this to `1` if your camera module has autofocus (v3) or `0` if it doesn't (v2).

Alternatively (recommended), you can create a file in the `server` folder called `.env` and store your environment variable values there.  See `env.example` for an example.  Don't commit `.env` to source control, as your Redis credentials should be considered a secret and managed as such!

### Running the Capture Script

With the setup steps completed, start the capture script as follows:

```
python3 capture.py
```

You should expect to see output similar to the following on startup (example using camera module v2.1):

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

Every so many seconds, the script will capture a new image. Expect to see output similar to the following:

```
Stored new image at image:1681923128
{'SensorTimestamp': 2058296354000, 'ScalerCrop': (0, 0, 3280, 2464), 'DigitalGain': 1.1096521615982056, 'ColourGains': (1.1879777908325195, 2.4338300228118896), 'SensorBlackLevels': (4096, 4096, 4096, 4096), 'AeLocked': False, 'Lux': 85.72087097167969, 'FrameDuration': 59489, 'ColourCorrectionMatrix': (1.6235777139663696, -0.38433241844177246, -0.23924528062343597, -0.5687134861946106, 2.019625425338745, -0.45091837644577026, -0.09334515780210495, -1.2399080991744995, 2.3332533836364746), 'AnalogueGain': 4.0, 'ColourTemperature': 2874, 'ExposureTime': 59413}
```

With the exception of the `Lux` value, he camera metadata isn't stored in Redis - it's just output for informational purposes.  If any of it is considered useful enough to keep, it should be easy to modify `capture.py` to add it to the Redis Hash that stores the image and associated data.

To stop the script, press Ctrl-C.