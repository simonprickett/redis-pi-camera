import io
import os
import redis
import time
from picamera2 import Picamera2, Preview
from libcamera import controls

# Picamera2 docs https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf
picam2 = Picamera2()
picam2.start_preview(Preview.NULL)
camera_config = picam2.still_configuration
# Tweak camera_config as needed before calling configure.
picam2.configure(camera_config)

# Connect to Redis.
redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

# Start the camera.
picam2.start()

# Put this in a loop or whatever you want to do with capturing images. Let's take
# an image every 10 seconds or so...

while True:
  image_data = io.BytesIO()

  # Take a picture and grab the metadata at the same time.
  image_metadata = picam2.capture_file(image_data, format="jpeg")
  current_timestamp = int(time.time())

  # Prepare data to save in Redis...
  redis_key = f"image:{current_timestamp}"
  data_to_save = dict()
  data_to_save["image_data"] = image_data.getvalue()
  data_to_save["timestamp"] = current_timestamp
  # Add any other flat name/value pairs you want to save into this dict 
  # e.g. light meter value, noise values, whatever really...

  # Store data in a Redis Hash (flat map of name/value pairs at a single
  # Redis key)
  redis_client.hset(redis_key, mapping = data_to_save)

  print(f"Stored new image at {redis_key}")

  # Optional - do something with the metadata if you want to.
  print(image_metadata)

  time.sleep(10)

# This code is unreachable but shows how to release the Redis client
# connection nicely should we want to say just take some pictures then
# exit...
redis_client.quit()
