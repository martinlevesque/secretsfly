#!/bin/sh

filesize=$(du -b /data/secretsfly-production.db | awk '{print $1}')

if [ $filesize -gt 1048576 ]; then
  echo "File is bigger than 1 MB."
  cp /workspace/db/secretsfly-current.db /data/secretsfly-production.db
else
  echo "File is smaller than 1 MB - $filesize bytes" > /workspace/sizelog.txt
fi
