#!/bin/bash
set -e

git pull

source venv/bin/activate

pip install -r requirements.txt

python3 manage.py migrate

npm ci --dev

python3 manage.py collectstatic

systemctl restart star-burger.service

echo "Success!"
