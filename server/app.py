from flask import Flask, send_file
import io
import os
import redis

API_ROUTE_PREFIX = "api"
IMAGE_KEY_PREFIX = "image"
IMAGE_DATA_FIELD_NAME = "image_data"
IMAGE_MIME_TYPE_FIELD_NAME = "mime_type"
IMAGE_TIMESTAMP_FIELD_NAME = "timestamp"
IMAGE_META_DATA_FIELDS = [
    IMAGE_TIMESTAMP_FIELD_NAME,
    IMAGE_MIME_TYPE_FIELD_NAME
    # Anything else that is captured on the Pi can go here.
]

# Initialise Flask
app = Flask(__name__)

# Connect to Redis using URL for environment.
redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

# Retrieve a list of all images in Redis.
@app.route(f"/{API_ROUTE_PREFIX}/images")
def get_all_images():
    all_images = []
    # Scan the Redis keyspace for all keys whose name begins with IMAGE_KEY_PREFIX.
    for img in redis_client.scan_iter(match=f"{IMAGE_KEY_PREFIX}:*", _type="HASH"):
        # Return only the timestamp part of the Redis key.
        all_images.append(img.decode('utf-8').removeprefix(f"{IMAGE_KEY_PREFIX}:"))

    # Most recent timestamp first...
    all_images.sort(reverse=True)
    return all_images

# Retrieve an image from Redis.
@app.route(f"/{API_ROUTE_PREFIX}/image/<image_id>")
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

# Retrieve image meta data from Redis.
@app.route(f"/{API_ROUTE_PREFIX}/data/<image_id>")
def get_image_data(image_id):
    # Look for the image meta data in Redis.
    image_meta_data = redis_client.hmget(f"{IMAGE_KEY_PREFIX}:{image_id}", IMAGE_META_DATA_FIELDS)

    if image_meta_data[0] is None:
      return f"Image {image_id} not found.", 404
    
    data_dict = dict()
    data_dict[IMAGE_TIMESTAMP_FIELD_NAME] = image_meta_data[0].decode("utf-8")
    data_dict[IMAGE_MIME_TYPE_FIELD_NAME] = image_meta_data[1].decode("utf-8")
    return data_dict

@app.route("/")
def home():
    return "TODO list all the images with links to their pages?"