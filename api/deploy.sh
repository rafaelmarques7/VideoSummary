#!/bin/bash

FUNCTION_NAME="f_video_summary"
REGION="europe-west1"
MEMORY="2048MB"
TIMEOUT=300

gcloud functions deploy $FUNCTION_NAME \
  --trigger-http \
  --runtime=python37 \
  --entry-point=main \
  --region=$REGION \
  --memory=$MEMORY \
  --timeout=$TIMEOUT
