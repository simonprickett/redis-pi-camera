from flask import Flask, send_file
import io
import os
import redis

IMAGE_KEY_PREFIX = "image"

app = Flask(__name__)

# Connect to Redis using URL for environment.
redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

# Retrieve an image from Redis.
@app.route("/image/<image_id>")
def get_image(image_id):
    image_data = redis_client.get(f"{IMAGE_KEY_PREFIX}:{image_id}")

    if image_data is None:
        return "Not found.", 404
    
    image_file = io.BytesIO(image_data)

    # Rewind the image file to the start...
    image_file.seek(0)

    return send_file(image_file, mimetype="image/jpeg")

@app.route("/")
def home():
    return "TODO list all the images with links to their pages?"