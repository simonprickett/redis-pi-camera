# TODO server README

![Front end displaying a selection of images](../server_component_running.png)

## Overview

This is a very basic "viewer" type front end that shows all of the images in the Redis database along with their metadata.

It isn't built with performance or scale in mind - a better implementation would use some sort of lazy loading and pagination strategy.

The server is built using Python and the Flask framework.  The front end web application is a single web page, styled with Bulma and using ES6 JavaScript with no JavaScript framework complexity / bloat.

## How it Works

TODO

## Setup

Before running the server, there are a couple of setup tasks to perform.

### Requirements

You need Python 3.7 or higher (I've tested this with Python 3.10).  To check your Python version:

```
python3 --version
```

If you need to upgrade your Python version, use your operating system's package manager or refer to [python.org](https://www.python.org/downloads/). 

### Create Virtual Environment & Install Dependencies

TODO

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

### Running the Server

Having got everything set up, start the server like so:

```
flask run
```

It should connect to port 5000, and when you point your browser at `http://localhost:5000/` you'll see the front end showing any images that have been stored in Redis.

