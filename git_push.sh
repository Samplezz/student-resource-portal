#!/bin/bash

# Remove existing origin
git remote remove origin

# Add new origin with token
git remote add origin https://$NEW_GITHUB_TOKEN@github.com/Samplezz/student-resource-portal.git

# Push to GitHub
git push -u origin main

echo "Push completed!"