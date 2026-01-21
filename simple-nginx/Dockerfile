FROM nginx:alpine

WORKDIR /etc/nginx

# Кладём нашу страницу вместо стандартной
COPY index.html /usr/share/nginx/html/index.html

# Кладём наш конфиг
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80


