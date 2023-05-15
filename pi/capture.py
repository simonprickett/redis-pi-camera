import io
import os
import redis
import time
from dotenv import load_dotenv
from picamera2 import Picamera2, Preview
from libcamera import controls

load_dotenv()

# Get the configurable values for how often to capture images and
# how long to keep them.
IMAGE_CAPTURE_FREQUENCY = int(os.getenv("IMAGE_CAPTURE_FREQUENCY"))
IMAGE_EXPIRY = int(os.getenv("IMAGE_EXPIRY"))

# Picamera2 docs https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf
picam2 = Picamera2()
picam2.start_preview(Preview.NULL)
camera_config = picam2.still_configuration
# For a v3 Camera Module, set continuous autofocus.
picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})
# Tweak camera_config as needed before calling configure.
picam2.configure(camera_config)

# Connect to Redis.
redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

# Start the camera.
picam2.start()

# Put this in a loop or whatever you want to do with capturing images. Let's take
# an image every so many seconds...

while True:
  # For the Camera Module 3, trigger an autofocus cycle.
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

  time.sleep(IMAGE_CAPTURE_FREQUENCY)

# This code is unreachable but shows how to release the Redis client
# connection nicely should we want to say just take some pictures then
# exit...
redis_client.quit()