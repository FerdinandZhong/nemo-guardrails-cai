#!/bin/bash
set -e
cd /home/cdsw

# Check if repo exists
if [ -d ".git" ]; then
  echo "Repository exists, pulling latest changes..."
  git pull origin main || git pull origin master
else
  echo "Repository not found, should be cloned during project creation"
  exit 1
fi

echo "Git sync completed successfully"
