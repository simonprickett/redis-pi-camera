from dotenv import load_dotenv
from flask import Flask, render_template, send_file
import base64
import io
import os
import redis
from redis.commands.search.query import Query

API_ROUTE_PREFIX = "api"
IMAGE_KEY_PREFIX = "image"
IMAGE_ID_FIELD_NAME = "id"
IMAGE_DATA_FIELD_NAME = "image_data"
IMAGE_MIME_TYPE_FIELD_NAME = "mime_type"
IMAGE_TIMESTAMP_FIELD_NAME = "timestamp"
IMAGE_LUX_FIELD_NAME = "lux"
IMAGE_META_DATA_FIELDS = [
    IMAGE_TIMESTAMP_FIELD_NAME,
    IMAGE_MIME_TYPE_FIELD_NAME,
    IMAGE_LUX_FIELD_NAME
    # Anything else that is captured on the Pi can go here.
]

STRING_ENCODING = "utf-8"

IMAGE_INDEX_NAME = "idx:images"

# Load environment variables from .env file.
load_dotenv()

# Initialise Flask
app = Flask(__name__)

# Connect to Redis using URL for environment.
redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

# Retrieve a list of all images in Redis.
@app.route(f"/{API_ROUTE_PREFIX}/images")
def get_all_images():
    all_images = []

    # Run a search query to get the latest 9 images and return
    # their data...
    # ft.search idx:images "*" return 3 timestamp lux mime_type sortby timestamp desc limit 0 9
    search_results = redis_client.ft(IMAGE_INDEX_NAME).search(Query("*").sort_by(IMAGE_TIMESTAMP_FIELD_NAME, False).paging(0, 9).return_fields(IMAGE_TIMESTAMP_FIELD_NAME, IMAGE_MIME_TYPE_FIELD_NAME, IMAGE_LUX_FIELD_NAME))

    for doc in search_results.docs:
        this_image = dict()
        this_image[IMAGE_ID_FIELD_NAME] = doc.id.removeprefix(f"{IMAGE_KEY_PREFIX}:")
        this_image[IMAGE_TIMESTAMP_FIELD_NAME] = int(doc.timestamp)
        this_image[IMAGE_MIME_TYPE_FIELD_NAME] = doc.mime_type
        this_image[IMAGE_LUX_FIELD_NAME] = int(doc.lux)
        all_images.append(this_image)

    return all_images

# Retrieve an image from Redis.
@app.route(f"/{API_ROUTE_PREFIX}/image/<image_id>")
def get_image(image_id):
    # Look for the image data in Redis.
    image_data = redis_client.json().get(f"{IMAGE_KEY_PREFIX}:{image_id}", "$.image_data", "$.mime_type")

    print(image_data)

    if image_data is None:
        return f"Image {image_id} not found.", 404
    
    # Load up the data into a file like data structure.
    image_file = io.BytesIO(base64.b64decode(image_data["$.image_data"][0]))

    # Rewind the image file to the start...
    image_file.seek(0)

    # Get the MIME type from the Redis response, and decode it from binary.
    return send_file(image_file, mimetype=image_data["$.mime_type"][0])

@app.route("/")
def home():
    return render_template("index.html")
