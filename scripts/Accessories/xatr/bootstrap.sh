#!/usr/bin/env bash

set -e

PROJECT_NAME="vision-pipeline"

echo "Creating project: $PROJECT_NAME"
mkdir -p $PROJECT_NAME
cd $PROJECT_NAME

# Core app structure

mkdir -p app/{sources,detector,serializer,sink,utils}
touch app/main.py app/pipeline.py app/config.py

# Sources

touch app/sources/{**init**.py,base.py,webcam.py,rtsp.py,video_file.py}

# Detector

touch app/detector/{**init**.py,yolo_detector.py,dto.py,mapper.py}

# Serializer

touch app/serializer/{**init**.py,json_serializer.py}

# Sink

touch app/sink/{**init**.py,base.py,mock_sink.py,framework_sink.py}

# Utils

touch app/utils/{**init**.py,logging.py,timing.py}

# Configs

mkdir -p configs
touch configs/{mac-dev.yaml,docker-rtsp.yaml,orin.yaml}

# Models and data

mkdir -p models data/samples data/outputs
touch models/README.md

# Tests

mkdir -p tests
touch tests/{test_mapper.py,test_serializer.py,test_replay.py}

# Scripts

mkdir -p scripts
touch scripts/{run_local.sh,run_docker.sh,bootstrap.sh}

# Root files

touch Dockerfile requirements.txt .env.example README.md .gitignore

echo "Project structure created successfully."

