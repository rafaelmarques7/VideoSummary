#!/bin/bash

FUNCTION_NAME="vis_function"
MEMORY="2048MB"
TIMEOUT=300
REGION="europe-west1"

gcloud functions deploy $FUNCTION_NAME \
  --trigger-http \
  --runtime=python37 \
  --entry-point=main \
  --region=$REGION \
  --memory=$MEMORY \
  --timeout=$TIMEOUT
