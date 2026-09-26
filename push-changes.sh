#!/bin/bash
cd "$(dirname "$0")"
echo "Pushing changes to GitHub..."
git push origin main
if [ $? -eq 0 ]; then
    echo "✓ Changes pushed successfully!"
    echo "Cloudflare Pages will auto-deploy the changes..."
else
    echo "✗ Push failed. Please check your GitHub credentials."
fi
