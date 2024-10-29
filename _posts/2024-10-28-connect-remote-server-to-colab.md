---
layout: post
title: 
date: 2024-10-28
description: 
tags: server, colab
categories: tutorial
thumbnail: 
featured: 
images:
  compare: true
  slider: true
# toc:
#   beginning: true
---

* For GPU support, with NVIDIA drivers and the NVIDIA container toolkit installed, use:
```bash
docker run --gpus=all -p 9000:8080 us-docker.pkg.dev/colab-images/public/runtime
```

* SSH tunneling to the remote server:
```bash
ssh -L 9000:localhost:9000 seclab-gpu
```
    - use this cmd to ensure the tunnel is open:
    ```bash
    ps aux | grep ssh
    ```


* connect to the local runtime in colab: enter the URL `http://localhost:9000/token=?` in the browser 

* check the GPU usage:

<div class="row justify-content-sm-center">
 <div class="col-sm-8 mt-3 mt-md-0">
    {% include figure.liquid loading="eager" path="assets/img/connect-remote-server-to-colab/local-colab.png" class="img-fluid rounded z-depth-1" zoomable=true %}
  </div>
</div>