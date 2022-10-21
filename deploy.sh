#!/bin/bash

export $(grep -v '^#' .env | xargs);

gcloud builds submit --tag gcr.io/multi-cluster-ingress-test/encryption:1.$1
docker push gcr.io/multi-cluster-ingress-test/encryption:1.$1

sed  "s/{VERSION}/$1/g;s/{PROJECT_ID}/$PROJECT_ID/g;s/{LOCATION_ID}/$LOCATION_ID/g;s/{KEY_RING_ID}/$KEY_RING_ID/g;s/{KEY_ID}/$KEY_ID/g;s/{ENCRYPTED_KEY}/$ENCRYPTED_KEY/g;s/{DESTINATION_BUCKET}/$DESTINATION_BUCKET/g"  Deployment.yaml_version > Deployment.yaml

gcloud run services replace Deployment.yaml --region southamerica-west1
