#!/bin/bash
# Push this folder to your GitHub repo. Run: bash push.sh
# It asks for your repo link, e.g. https://github.com/YOURNAME/reel-factory.git
set -e
echo "Paste your GitHub repo link (from github.com/new, Step 1):"
read -r REPO
if [ -z "$REPO" ]; then echo "No link given. Stopping."; exit 1; fi
git init -b main
git add .
git commit -m "Reel factory: topic or script in, Hindi reel out" || true
git remote remove origin 2>/dev/null || true
git remote add origin "$REPO"
git push -u origin main
echo "Done. Refresh your repo page on GitHub to check the files are there."
