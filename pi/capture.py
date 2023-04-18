import io
import os
import redis
import time
# Picamera2 isn't in requirements.txt as it is pre-installed on Raspberry Pi OS
# Bullseye or later.  
from picamera2 import Picamera2

# Picamera2 docs https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf
picam2 = Picamera2()
camera_config = picam2.create_preview_configuration()
# Tweak camera_config as needed before calling configure.
picam2.configure(camera_config)

# Connect to Redis
redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

picam2.start()

# Put this in a loop or whatever you want to do with capturing images. Let's take
# an image every 10 seconds or so...

while True:
  image_data = io.BytesIO()
  picam2.capture_file(image_data, format="jpeg")
  current_timestamp = int(time.time())

  # TODO move this to a hash with metadata fields, and use the timestamp in the key name...
  redis_key = f"image:{current_timestamp}"
  redis_client.set(redis_key, image_data.getvalue())

  print(f"Stored new image at {redis_key}")
  time.sleep(10)

# This code is unreachable but shows how to release the Redis client
# connection nicely should we want to say just take some pictures then
# exit...
redis_client.quit()