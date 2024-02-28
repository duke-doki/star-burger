#!/bin/bash
set -e

git pull

source venv/bin/activate

pip install -r requirements.txt

python3 manage.py migrate

npm ci --dev

python3 manage.py collectstatic

systemctl restart star-burger.service

set -a
[ -f .env ] && . .env
set +a

curl --request POST \
     --url https://api.rollbar.com/api/1/deploy \
     --header "X-Rollbar-Access-Token: $ROLLBAR_TOKEN" \
     --header 'accept: application/json' \
     --header 'content-type: application/json' \
     --data '
{
  "environment": "production",
  "revision": "'$(git log -n 1 --pretty=format:"%H")'"
}
'

echo "Success!"
