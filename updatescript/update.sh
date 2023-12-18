#!/bin/bash

# Переменные
SERVICE_NAME="new-oncall"
NGINX_CONTAINER_NAME="nginx"
SERVICE_NEW_IMAGE="denuar/oncall:1.0"

docker cp ../nginx/new_nginx.conf nginx:/etc/nginx/nginx.conf
docker pull ${SERVICE_NEW_IMAGE}

container_id=$(docker compose -f ../docker-compose.yml up -d ${SERVICE_NAME})
container_status=$(docker inspect -f '{{.State.Status}}' "$container_id")

echo "Контейнер ${SERVICE_NAME}:${container_status}."

docker cp ../nginx/fifty_fifty_nginx.conf nginx:/etc/nginx/nginx.conf
docker exec ${NGINX_CONTAINER_NAME}  nginx -s reload -c nginx.conf
echo "Контейнер ${SERVICE_NAME} добавлен в балансировку"

echo "Нажмите Esc для отката к старым настройкам или же любую другую для перехода на новую версию"
read -r -s -n 1 key

if [ "$key" == $'\033' ]; then
  docker cp ../nginx/nginx.conf nginx:/etc/nginx/nginx.conf
  docker exec ${NGINX_CONTAINER_NAME}  nginx -s reload -c nginx.conf
  echo "Контейнер ${SERVICE_NAME} выведен из балансировки"
else
  docker cp ../nginx/new_nginx.conf nginx:/etc/nginx/nginx.conf
  docker exec ${NGINX_CONTAINER_NAME}  nginx -s reload -c nginx.conf
  echo "Контейнер cо старой версией выведен из балансировки"
  docker compose up -d --scale new-oncall=3 --no-recreate new-oncall
  docker exec ${NGINX_CONTAINER_NAME}  nginx -s reload -c nginx.conf
  echo "Контейнер успещно заскейлен для обеспечения отказоустойчивости"
fi


