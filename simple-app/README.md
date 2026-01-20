## Simple CI/CD Demo App

Мини-приложение на Python для демонстрации CI/CD:

- `app.py` — простой HTTP-сервер, который отвечает текстом.
- `Dockerfile` — собирает Docker-образ `python:3.12-slim` + наш `app.py`.

Локальный запуск (из Ubuntu):

```bash
cd /mnt/d/DevOpsPractice/simple-app

sudo docker build -t ci-demo-app .
sudo docker run --rm -p 8000:8000 ci-demo-app
```

Потом в браузере: `http://localhost:8000`.


