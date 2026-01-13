#!/bin/bash

# Build the image
docker build -t poshbullet-integrated .
# Run the container (mapping both ports)
docker run -p 5000:5000 -p 5001:5001 poshbullet-integrated