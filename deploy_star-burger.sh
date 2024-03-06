#!/bin/bash
set -e

source ~/.nvm/nvm.sh

git pull

CURRENT_NODE_VERSION=$(nvm current)

source venv/bin/activate

pip install -r requirements.txt

python3 manage.py migrate

nvm use 16.16.0

npm ci --dev

./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"

echo "yes" | python3 manage.py collectstatic --no-input

sudo systemctl restart star-burger.service

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

nvm use $CURRENT_NODE_VERSION

echo "Success!"
