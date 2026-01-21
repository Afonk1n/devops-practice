## Практика 01 — базовый DevOps-стек

Эта папка — просто «ярлык» на то, что ты уже сделал в корне репо.  
Чтобы не ломать пути и не копировать файлы, мы оставляем всё на своих местах, но логически считаем это **первой практикой**.

В неё входят:

- `devops_interview_crash_day.md` — общий план однодневного разгона.
- `cheatsheets/` — шпаргалки:
  - `linux_basics.md`
  - `docker_basics.md`
  - `kubernetes_basics.md`
  - `git_basics.md`
  - `ci_cd_basics.md`
- `simple-nginx/` — простой Nginx в Docker:
  - `Dockerfile`, `index.html`, `nginx.conf`, `README.md`.
- `simple-app/` — Python-приложение + Docker + CI:
  - `app.py`, `Dockerfile`, `README.md`.
  - `.github/workflows/docker-ci.yml` — GitHub Actions для сборки Docker-образа.
- `k8s-demo/` — Kubernetes-манифесты:
  - `deployment.yaml`, `service.yaml`, `ingress.yaml`, `configmap.yaml`, `secret.yaml`.
- `final_overview.md` — итоговая схема по первой практике.
- `interview_script.md` — скрипт для собеса на основе первой практики.

Дальше мы создаём отдельную директорию `laravel-app/` под **вторую, более «боевую» практику** уже на Laravel.


