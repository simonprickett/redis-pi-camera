# Experiments with Redis and the Raspberry Pi Camera Module

## Overview 

This repository contains an example application that demonstrates how to capture images from a Raspberry Pi using the camera module, store them in Redis Hashes and render them in a web application.

Here's what the front end looks like when a few images have been captured by the Raspberry Pi...

TODO IMAGE

And here's a Raspberry Pi with a camera attached:

TODO IMAGE

## Components of the Demo

This repository contains two components:

* **Image capture component:** TODO
* **Front end component:** TODO

Details of how each component works, how to configure and run it can be found in the README files in each of the above folders.

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

## (Optional, but Recommended): RedisInsight

RedisInsight is a free graphical management and database browsing tool for Redis. You don't need it to look at how the application stores data in Redis (you can use redis-cli if you prefer) but I'd recommend it as it's much easier to get an overall picture of the state of the database with a graphical tool.  RedisInsight runs as a desktop application on your Mac, Windows or Linux machine.

[Download RedisInsight here](https://redis.io/docs/ui/insight/).

If you're using the Docker compose file provided with this project to run Redis Stack, you can also access a web based version of RedisInsight with no additional software to install.  With the Docker container running, navigate to `http://localhost:8001` to use the web version.
