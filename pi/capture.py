import io
import os
import redis
import time
import RPi.GPIO as GPIO
from dotenv import load_dotenv
from picamera2 import Picamera2, Preview
from libcamera import controls
from signal import pause

load_dotenv()

# Get the configurable values for how often to capture images and
# how long to keep them.
IMAGE_EXPIRY = int(os.getenv("IMAGE_EXPIRY"))
CAMERA_AUTOFOCUS = os.getenv("CAMERA_AUTOFOCUS") == "1"
SOUND_SENSOR_PIN = int(os.getenv("SOUND_SENSOR_PIN"))
SOUND_SENSOR_DEBOUNCE_MILLIS = int(os.getenv("SOUND_SENSOR_DEBOUNCE_MILLIS"))

# Picamera2 docs https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf
picam2 = Picamera2()
picam2.start_preview(Preview.NULL)
camera_config = picam2.still_configuration

# For a v3 Camera Module, set continuous autofocus.
if CAMERA_AUTOFOCUS == True:
    picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})

# Tweak camera_config as needed before calling configure.
picam2.configure(camera_config)

# Connect to Redis.
redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

# Start the camera.
picam2.start()

# Callback for when the sound sensor triggers
def on_sound(channel):
    # The sound sensor triggered, take a picture!

    # For the Camera Module 3, trigger an autofocus cycle.
    if CAMERA_AUTOFOCUS == True:
        picam2.autofocus_cycle()

    image_data = io.BytesIO()

    # Take a picture and grab the metadata at the same time.
    image_metadata = picam2.capture_file(image_data, format="jpeg")
    current_timestamp = int(time.time())

    # Prepare data to save in Redis...
    redis_key = f"image:{current_timestamp}"
    data_to_save = dict()
    data_to_save["image_data"] = image_data.getvalue()
    data_to_save["timestamp"] = current_timestamp
    data_to_save["mime_type"] = "image/jpeg"
    data_to_save["lux"] = int(image_metadata["Lux"])
    # Add any other flat name/value pairs you want to save into this dict
    # e.g. light meter value, noise values, whatever really...

    # Store data in a Redis Hash (flat map of name/value pairs at a single
    # Redis key), also set an expiry time for the image.
    pipe = redis_client.pipeline(transaction=False)
    pipe.hset(redis_key, mapping = data_to_save)
    pipe.expire(redis_key, IMAGE_EXPIRY)
    pipe.execute()

    print(f"Stored new image at {redis_key}")

    # Optional - do something with the metadata if you want to.
    print(image_metadata)

# Set up the sound sensor.
GPIO.setmode(GPIO.BCM)
GPIO.setup(SOUND_SENSOR_PIN, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.add_event_detect(SOUND_SENSOR_PIN, GPIO.RISING, bouncetime = SOUND_SENSOR_DEBOUNCE_MILLIS, callback = on_sound)

# Do nothing and wait for events to trigger camera callback.
pause()

# This code is unreachable but shows how to release the Redis client
# connection nicely should we want to say just take some pictures then
# exit...
redis_client.quit()