# Experiments with Redis and the Raspberry Pi Camera Module

## Overview 

This repository contains an example application that demonstrates how to capture images from a Raspberry Pi using the camera module, store them in [Redis Hashes](https://redis.io/docs/data-types/hashes/) and render them in a web application.

Here's what the front end looks like when a few images have been captured by the Raspberry Pi...

![Front end showing captured images](server_component_running.png)

(Images are somewhat out of focus as the camera I am using doesn't have auto focus and I didn't adjust its position for these pics, they were just test data!)

And here's a Raspberry Pi with a camera attached:

![Raspberry Pi 3 with Camera Module attached](raspberry_pi_3_with_camera_module.jpg)

## Components of the Demo

This repository contains two components:

* **[Image capture component](pi/):** This is written in Python and runs on a Raspberry Pi with a camera module attached.  It takes a new picture every so often and stores it, plus some basic metadata, in Redis.  Python was the obvious implementation choice here as Raspberry Pi provides an excellent Python library for their camera modules. See the `pi` folder for full details.
* **[Front end component](server/):** This comprises a server written in Python using the Flask framework.  It reads data from Redis and uses a HTML front end to display it in a grid view.  It uses HTML, JavaScript and the Bulma framework.  These were all arbitrary choices - this component could equally be built with Node.js and Express for example.  See the `server` folder for full details.

Details of how each component works including how to configure and run it can be found in the README files in each of the above folders.

## Redis

Both components need to be connected to the same Redis instance to talk to each other.  Right now, this demo works on any Redis 5 or higher server.  The enclosed Docker Compose file uses Redis Stack - this is to allow for future enhancements to the application to use Stack's Search capability.

If you want to use Docker, start Redis like this:

```
docker-compose up -d
```

When you're done with the Docker container, stop it like this:

```
docker-compose down
```

With the container running, you can access the [Redis CLI](https://redis.io/docs/ui/cli/) using this command:

```
docker exec -it redispiimages redis-cli
```

See the RedisInsight section of this document if you're interested in a graphical alternative to the Redis CLI interface.

You'll need to make sure that both components of the application can connect to your Redis instance.  See details in each component's README.

This project will also work with a free Redis Stack cloud instance from Redis (the company).  To use this, [sign up here](https://redis.com/try-free/) and make a note of your Redis host, port and password.  You'll need those to configure each component.

## The Redis Data Model and Key Naming Strategy

The application stores each image plus associated metadata in its own [Redis Hash](https://redis.io/docs/data-types/hashes/).  A Hash in Redis can be thought of as a flat map of name/value properties.  Each Hash is stored in its own key in Redis.

The key naming strategy is as follows.  Each Hash's key has a fixed prefix `image:` followed by the [UNIX timestamp](https://en.wikipedia.org/wiki/Unix_time) representing the time that the image was captured.

For example the key `image:1681844748` would contain a Hash with data for an image taken on Tuesday 18th April 2023 at 7:05:48pm GMT.

Each key contains a hash with the following name/value pairs:

* `mime_type`: The [MIME type](https://en.wikipedia.org/wiki/Media_type) for the captured image data.  This will always be `image/jpeg` unless you change it and the image capture format in the `capture.py` script.
* `timestamp`: The [UNIX timestamp](https://en.wikipedia.org/wiki/Unix_time) that the image was captured at, as recoded from the Raspberry Pi's clock.  This will be the same value as the timestamp in the key name.
* `image_data`: A binary representation of the bytes for the image captured by the camera.  This will be a [JPEG image](https://en.wikipedia.org/wiki/JPEG) unless you change the capture format in `capture.py`.

Here's a complete example, with the image data truncated for brevity:

```
> HGETALL image:1681843615
1) "mime_type"
2) "image/jpeg"
3) "timestamp"
4) "1681843615"
5) "image_data"
6) "\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00...
```
With the camera that I used ([Raspberry Pi Camera Module 2.1](https://www.raspberrypi.com/products/camera-module-v2/) capturing at 3280x2464 pixels - configurable in `capture.py`) you can expect each Hash to require around 2Mb of RAM in Redis.

## (Optional, but Recommended): RedisInsight

RedisInsight is a free graphical management and database browsing tool for Redis. You don't need it to look at how the application stores data in Redis (you can use redis-cli if you prefer) but I'd recommend it as it's much easier to get an overall picture of the state of the database with a graphical tool.  RedisInsight runs as a desktop application on your Mac, Windows or Linux machine.

[Download RedisInsight here](https://redis.io/docs/ui/insight/).

If you're using the Docker compose file provided with this project to run Redis Stack, you can also access a web based version of RedisInsight with no additional software to install.  With the Docker container running, navigate to `http://localhost:8001` to use the web version.
