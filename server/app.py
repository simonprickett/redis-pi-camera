from flask import Flask, send_file
import io
import os
import redis

IMAGE_KEY_PREFIX = "image"
IMAGE_DATA_FIELD_NAME = "image_data"
IMAGE_MIME_TYPE_FIELD_NAME = "mime_type"
# TODO might need other things, timestamp?

# Initialise Flask
app = Flask(__name__)

# Connect to Redis using URL for environment.
redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

# Retrieve an image from Redis.
@app.route("/image/<image_id>")
def get_image(image_id):
    # Look for the image data in Redis.
    image_data = redis_client.hmget(f"{IMAGE_KEY_PREFIX}:{image_id}", [ IMAGE_DATA_FIELD_NAME, IMAGE_MIME_TYPE_FIELD_NAME ])

    if image_data[0] is None:
        return f"Image {image_id} not found.", 404
    
    # Load up the data into a file like data structure.
    image_file = io.BytesIO(image_data[0])

    # Rewind the image file to the start...
    image_file.seek(0)

    # Get the MIME type from the Redis response, and decode it from binary.
    return send_file(image_file, mimetype=image_data[1].decode("utf-8"))

@app.route("/")
def home():
    return "TODO list all the images with links to their pages?"