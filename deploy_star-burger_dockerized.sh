#!/bin/bash
set -e

git pull

docker compose down
docker compose up -d --build

docker compose exec django_container python manage.py migrate

docker compose exec django_container python manage.py collectstatic --no-input

docker compose restart django_container

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

echo "Deployment successful!"
