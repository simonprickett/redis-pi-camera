# Server Component / Front End

![Front end displaying a selection of images](../server_component_running.png)

(Images are somewhat out of focus as the camera I am using doesn't have auto focus and I didn't adjust its position for these pics, they were just test data!)

## Overview

This is a very basic "viewer" type front end that shows all of the images in the Redis database along with their metadata.

It isn't built with performance or scale in mind - a better implementation would use some sort of lazy loading and pagination strategy.

The server is built using Python and the [Flask framework](https://flask.palletsprojects.com/).  The front end web application is a single web page, styled with [Bulma](https://bulma.io/) and using vanilla ES6 JavaScript with no JavaScript framework complexity / bloat.

## How it Works

### Structure

First, let's take a look at how the project is organised.

* All of the code for the server is in a single file: `app.py`.  This uses the Flask framework and maintains a connection to Redis.
* The HTML for the front end is a Flask template, contained in `templates/index.html`.  The application doesn't actually do any templating so `index.html` is essentially a static file, but I set it up as a template in case you want to build on this start point and do something dynamic on the home page.  It also means that I could use a tiny bit of templating to create the `<script>` tag that load the JavaScript for the front end...
* The JavaScript that runs on the front end is a static file, contained in `static/app.js`.  Flask knows how to serve this when asked for a URL `/static/app.js`.  You can see how this is resolved at the bottom of the `index.html` file:

```html
<script type="text/javascript" src="{{ url_for('static', filename = 'app.js') }}" defer></script>
```

* There is no CSS file for this project, all CSS is provided by the [Bulma framework](https://bulma.io/).  It's included in the `<head>` of `index.html` and hosted on a CDN:

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma@0.9.4/css/bulma.min.css">
```

### The Flask Application

The server-side Flask application is contained entirely in the `app.py` file.  This will be a high level walk through - if you'd like to lean more about Flask, check out the [excellent documentation](https://flask.palletsprojects.com/en/2.2.x/quickstart/).

On startup, the code initialises Flask and connects to Redis:

```python
app = Flask(__name__)
redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
```

I've chosen to configure the Redis client not to decode the bytes responses from Redis (by omitting `decode_responses=True`).  This is because we'll need the raw image data stored in Redis without decoding.  So whenever we read String data from Redis, we will need to decode it back to a UTF-8 representation using `.decode("utf-8")` and you will see this throughout the code.

The rest of the application is broken down into code for 4 different routes as follows:

#### Getting the Home Page

This is very simple.  Whenever `/` is requested, simply return the contents of `templates/index.html` processing any template directives in there.  The only logic in the index file is one line that works out the relative path to the JavaScript file when including it in the HTML returned.  This route returns a HTML page that links to the JavaScript file and the Bulma CSS file.

Bulma's CSS is hosted on an external CDN so there's no code here to serve it.  Flask handles serving static files for us, so we don't need additional code for the JavaScript file either.

Here's the entire route:

```python
@app.route("/")
def home():
    return render_template("index.html")
```

#### Getting a List of Available Images

We need an API type route that returns a JSON array containing the IDs of all of the images in Redis.  This basically means we want the timestamp part of every key in Redis that begins with `image:`.

In this basic demonstration, I've used the Redis [`SCAN` command](https://redis.io/commands/scan/) to get these in a reasonably scalable manner for a simple demonstration.  To narrow down what's returned from the scan, I'm passing in a key prefix of `image:` and telling Redis I only want keys whose data type is `HASH`.

The code works by iterating over the key names returned by `SCAN`, adding them to a list.  Before adding each key name, it's decoded to a UTF-8 string and the key prefix `image:` is removed as the front end doesn't need to know about this and it also saves a little network bandwidth between the Flask server and front end.

```python
@app.route(f"/{API_ROUTE_PREFIX}/images")
def get_all_images():
    all_images = []
    # Scan the Redis keyspace for all keys whose name begins with IMAGE_KEY_PREFIX.
    for img in redis_client.scan_iter(match=f"{IMAGE_KEY_PREFIX}:*", _type="HASH"):
        # Return only the timestamp part of the Redis key.
        all_images.append(img.decode(STRING_ENCODING).removeprefix(f"{IMAGE_KEY_PREFIX}:"))

    # Most recent timestamp first...
    all_images.sort(reverse=True)
    return all_images
```

Before returning the data to the front end, it's sorted in reverse order, so that the most recent image timestamp is first.

With a really big dataset, we'd want to do something better than this.  At minimum, we'd want to page through the dataset in multiple calls to this route.  We might also want to specify some search and ordering criteria based on metadata about each image held in Redis.  For that, the [Search capability of Redis Stack](https://redis.io/docs/stack/search/) would be a good approach and I may update this repository with that in future.

#### Getting the Metadata for a Specific Image

TODO

#### Getting the Binary Data for a Specific Image

This route is unlike the others in that it doesn't return a text-based response.  Here, given the timestamp ID for an image, we want to return the data for that image, encoded in a way that the browser will recognise it as an image and render it correctly.

TODO...

### The Web Front End

When the browser initially receives the HTML for the home page, there are no images contained in it.  The image details get loaded into the `div` whose ID is `imageArea` dynamically when the JavaScript runs.  Initially, it's just an empty `div`:

```html
<div class="columns is-flex-wrap-wrap" id="imageArea">
```

The `columns` and `is-flex-wrap-wrap` classes are defined in Bulma and give us a flexbox type grid.

The JavaScript file is loaded with the `defer` option, so it only starts to execute after the browser has parsed the page's HTML.  Once it starts to execute, it requests the `/api/images` route from the Flask server.

If no images are returned, a notification is shown.  This is already in the HTML for the page, but is initially hidden.  It's shown as needed by removing the Bulma helper class `is-hidden`:

```javascript
  const noImagesNotification = document.getElementById('noImagesNotification');
  noImagesNotification.classList.remove('is-hidden');
```

If the Flask server returned a JSON array of image IDs, we loop over it.  In each loop iteration, we get the ID (UNIX timestamp) of the image, and use that to request more information about that specific image from the Flask server:

```javascript
const imageDetailResponse = await fetch(`${API_PREFIX}/data/${imageId}`)
const imageData = await imageDetailResponse.json();
```

Using the image ID (timestamp) we can also work out what URL we need to load the image from the Flask server:

```javascript
const imageUrl = `/${API_PREFIX}/image/${imageId}`;
```

With the value in `imageUrl` and metadata values in `imageData`, we can then use a template string and a HTML fragment to create the HTML we need to display this item on the page:

```javascript
const imageHTML = `
  <div class="card m-4">
    <div class="card-image">
      <figure class="image is-4by3">
        <img src="${imageUrl}" alt="Image ${imageId}">
      </figure>
    </div>
    <div class="card-content">
      <div class="media">
        <div class="media-content">
          <p class="title is-4">${new Date(parseInt(imageId * 1000, 10)).toUTCString()}</p>
        </div>
      </div>

      <div class="content">
        <ul>
          ${renderImageData(imageData)}
        </ul>
      </div>
    </div>
  </div>
</div>`;
```

The two complexities worth looking at in the above are:

1. I wanted to display the timestamp that the picture was taken in a meaningful format.  To do this, the timestamp gets multiplied by 1000 to make it a milliseconds timestamp.  Javacript has a `Date` constructor that accepts these, and the resulting `Date` object can be converted to a decent human readable date using `toUTCString`.  So the code to display the date is: `new Date(parseInt(imageId * 1000, 10)).toUTCString()`.
1. I also wanted to display all image metadata, without hard coding the names of the metadata fields.  This is so that the front end will just display anything passed to it, and adding more metadata in the capture script won't require code changes in the front end.  To do this, I created a utility function that takes an object containing name/value pairs and renders them out as a HTML list items:

```javascript
function renderImageData(dataItems) {
  let html = '';
  for (const k in dataItems) {
    html = `${html}<li><span class="has-text-weight-bold">${k}:</span> ${dataItems[k]}</li>`;
  }

  return html;
}
```

This is then called from the template string like so:

```javascript
<div class="content">
  <ul>
    ${renderImageData(imageData)}
  </ul>
</div>
```

Now, all that remains is to add the HTML into the `div` whose ID is `imageArea` and move on to the next item in the loop until we're done:

```javascript
// Before the loop so we aren't looking this up each iteration...
const imageArea = document.getElementById('imageArea');

// In the loop...
imageArea.innerHTML = `${imageArea.innerHTML}${imageHTML}`;
```

## Setup

Before running the server, there are a couple of setup tasks to perform.

### Requirements

You need Python 3.7 or higher (I've tested this with Python 3.10).  To check your Python version:

```
python3 --version
```

If you need to upgrade your Python version, use your operating system's package manager or refer to [python.org](https://www.python.org/downloads/). 

### Create Virtual Environment & Install Dependencies

Next, create and activate a Python virtual environment, then install the dependencies. These are the [Flask framework](https://flask.palletsprojects.com/) and [redis-py Redis client](https://github.com/redis/redis-py):

```
python3 -m venv venv
. ./venv/bin/activate
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

Alternatively, you can create a file in the `server` folder called `.env` and store your environment variable values there.  See `env.example` for an example.  Don't commit `.env` to source control, as your Redis credentials should be considered a secret and managed as such!

### Running the Server

Having got everything set up, start the server like so:

```
flask run
```

You'll see output similar to the following:

```
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

The server should have connected to port 5000. When you point your browser at `http://localhost:5000/` you'll see the front end showing any images that have been stored in Redis.

Whenever you are done using the server, press Ctrl-C to terminate it.