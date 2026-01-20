## Простое Nginx-приложение в Docker

Мини-проект для подготовки к собесу DevOps: один `Dockerfile` и одна страничка `index.html`.

### Структура

- `Dockerfile` — базовый образ `nginx:alpine`, копируем свою страницу.
- `index.html` — простая страница, которую отдаёт Nginx.

### Команды (из WSL/Ubuntu)

```bash
cd /mnt/d/DevOpsPractice/simple-nginx

# Собрать образ
docker build -t devops-nginx .

# Запустить контейнер
docker run --rm -p 8080:80 devops-nginx
```

После запуска открой в браузере на Windows: `http://localhost:8080` — должна открыться наша страница.


