---
layout: post
title: docker cookers
date: 2024-11-11
description: 
tags: cooker, usage
categories: docker 
thumbnail: 
featured: 
images:
  compare: true
  slider: true
toc:
  beginning: true
---


Usage:  docker [OPTIONS] COMMAND
---

A self-sufficient runtime for containers

## Common Commands:
```plaintext
run         Create and run a new container from an image
exec        Execute a command in a running container
ps          List containers
build       Build an image from a Dockerfile
pull        Download an image from a registry 
push        Upload an image to a registry  
images      List images  
login       Log in to a registry  
logout      Log out from a registry  
search      Search Docker Hub for images  
version     Show the Docker version information  
info        Display system-wide information  
```

## Management Commands:
```plaintext
  builder     Manage builds
  buildx*     Docker Buildx (Docker Inc., v0.11.2)
  compose*    Docker Compose (Docker Inc., v2.21.0)
  container   Manage containers
  context     Manage contexts
  image       Manage images
  manifest    Manage Docker image manifests and manifest lists
  network     Manage networks
  plugin      Manage plugins
  system      Manage Docker
  trust       Manage trust on Docker images
  volume      Manage volumes
```

## Swarm Commands:
```plaintext
  swarm       Manage Swarm
```

## Commands:
```plaintext
  attach      Attach local standard input, output, and error streams to a running container
  commit      Create a new image from a container's changes
  cp          Copy files/folders between a container and the local filesystem
  create      Create a new container
  diff        Inspect changes to files or directories on a container's filesystem
  events      Get real time events from the server
  export      Export a container's filesystem as a tar archive
  history     Show the history of an image
  import      Import the contents from a tarball to create a filesystem image
  inspect     Return low-level information on Docker objects
  kill        Kill one or more running containers
  load        Load an image from a tar archive or STDIN
  logs        Fetch the logs of a container
  pause       Pause all processes within one or more containers
  port        List port mappings or a specific mapping for the container
  rename      Rename a container
  restart     Restart one or more containers
  rm          Remove one or more containers
  rmi         Remove one or more images
  save        Save one or more images to a tar archive (streamed to STDOUT by default)
  start       Start one or more stopped containers
  stats       Display a live stream of container(s) resource usage statistics
  stop        Stop one or more running containers
  tag         Create a tag TARGET_IMAGE that refers to SOURCE_IMAGE
  top         Display the running processes of a container
  unpause     Unpause all processes within one or more containers
  update      Update configuration of one or more containers
  wait        Block until one or more containers stop, then print their exit codes
```

## Global Options:
```plaintext
      --config string      Location of client config files (default
                           "/home/yutong/.docker")
  -c, --context string     Name of the context to use to connect to the
                           daemon (overrides DOCKER_HOST env var and
                           default context set with "docker context use")
  -D, --debug              Enable debug mode
  -H, --host list          Daemon socket to connect to
  -l, --log-level string   Set the logging level ("debug", "info",
                           "warn", "error", "fatal") (default "info")
      --tls                Use TLS; implied by --tlsverify
      --tlscacert string   Trust certs signed only by this CA (default
                           "/home/yutong/.docker/ca.pem")
      --tlscert string     Path to TLS certificate file (default
                           "/home/yutong/.docker/cert.pem")
      --tlskey string      Path to TLS key file (default
                           "/home/yutong/.docker/key.pem")
      --tlsverify          Use TLS and verify the remote
  -v, --version            Print version information and quit
```

## What is docker, image, and container?
- Docker: an open source project that uses images and containers to package and deploy software efficiently. 
- Image: aka docker image. A read-only file that contains the code, libraries, dependencies, tools, and other files needed to run an application in a Docker container. 
- Container: aka docker container. Containers are isolated environments where an application runs without affecting the rest of the system.
- Dockerhub: You can store Docker images in a public or private Docker registry, where other team members or end-users can access them. Docker Hub is the default global marketplace for storing and distributing images. 


