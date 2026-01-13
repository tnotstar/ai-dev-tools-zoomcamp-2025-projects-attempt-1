#!/bin/bash

# Build the image
docker build -t poshbullet-integrated .
# Run the container (mapping only frontend port)
# Backend port 5001 is internal only, accessed by frontend via localhost
docker run -p 8080:8080 poshbullet-integrated