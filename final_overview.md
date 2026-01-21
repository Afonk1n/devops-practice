## Общая картина: от кода до Kubernetes

Это конспект именно по тому, что ты уже руками сделал в этом проекте.

### 1. Локальная разработка и Git

- Пишем/меняем код:
  - `simple-app/app.py` — простое HTTP-приложение на Python.
  - `simple-nginx` — статическая страничка + `nginx.conf`.
- Управление версиями через Git:
  - `git status` — посмотреть изменения.
  - `git add .` — добавить в staging.
  - `git commit -m "..."` — зафиксировать изменения.
  - `git push origin master` — отправить на GitHub.

### 2. Упаковка в Docker

**Цель:** иметь воспроизводимое окружение, которое можно запустить где угодно.

- Dockerfile для Python-приложения (`simple-app/Dockerfile`):
  - базовый образ: `FROM python:3.12-slim`;
  - копируем код: `COPY app.py /app/app.py`;
  - указываем порт: `EXPOSE 8000`;
  - команда запуска: `CMD ["python", "app.py"]`.
- Dockerfile для Nginx (`simple-nginx/Dockerfile`):
  - `FROM nginx:alpine`;
  - кладём свою страницу: `COPY index.html /usr/share/nginx/html/index.html`;
  - кладём свой конфиг: `COPY nginx.conf /etc/nginx/conf.d/default.conf`;
  - `EXPOSE 80`.

**Команды:**

- Сборка:
  - `sudo docker build -t ci-demo-app ./simple-app`;
  - `sudo docker build -t devops-nginx ./simple-nginx`.
- Запуск:
  - `sudo docker run --rm -p 8000:8000 ci-demo-app`;
  - `sudo docker run --rm -p 8080:80 devops-nginx`.

Результат:
- `http://localhost:8000` — отвечает Python-сервис;
- `http://localhost:8080` — отдаёт страницу из Nginx-контейнера.

### 3. CI с GitHub Actions

**Цель:** при каждом push проверять, что Docker-образ собирается.

- Файл `.github/workflows/docker-ci.yml`.
- Триггеры:
  - `on: push` и `on: pull_request` для ветки `master`.
- Job `build`:
  - `actions/checkout@v4` — забирает код;
  - `docker/setup-buildx-action@v3` — готовит окружение Docker;
  - `docker/build-push-action@v6`:
    - `context: ./simple-app`;
    - `push: false` (только сборка);
    - `tags: ci-demo-app:latest`.

Логика:
- разработчик пушит в `master`;
- GitHub Actions автоматически пытается собрать Docker-образ;
- если Dockerfile/код сломан — сборка красная.

### 4. Kubernetes-кластер (Docker Desktop)

**Цель:** запустить приложение уже не как один контейнер, а как управляемый набор Pod-ов с балансировкой.

- Кластер:
  - включён в Docker Desktop (контекст `docker-desktop`);
  - проверка: `kubectl get nodes` → `docker-desktop Ready`.

**Наши манифесты (`k8s-demo`):**

- `configmap.yaml`:
  - `ConfigMap demo-config` с ключом `APP_ENV=production`.
- `secret.yaml`:
  - `Secret demo-secret` с ключом `APP_SECRET` (base64).
- `deployment.yaml`:
  - `Deployment demo-nginx`;
  - `replicas: 2` — две копии Pod-a;
  - контейнер `nginx:alpine`, порт `80`;
  - переменные окружения:
    - `APP_ENV` из ConfigMap `demo-config`;
    - `APP_SECRET` из Secret `demo-secret`.
- `service.yaml`:
  - `Service demo-nginx` типа `ClusterIP`;
  - `selector: app=demo-nginx`;
  - `port: 80`, `targetPort: 80`.
- `ingress.yaml`:
  - `Ingress demo-nginx`;
  - правило: host `demo.local` → Service `demo-nginx:80`.

**Команды:**

- Применение:
  - `kubectl apply -f .` (из `k8s-demo`).
- Проверка:
  - `kubectl get deployments`;
  - `kubectl get pods`;
  - `kubectl get svc`;
  - `kubectl get ingress`.
- Детали Pod-а:
  - `kubectl describe pod demo-nginx-...`;
  - видно образ, IP, env-переменные из ConfigMap/Secret, состояние контейнера.
- Логи:
  - `kubectl logs demo-nginx-...`.
- Port-forward:
  - `kubectl port-forward svc/demo-nginx 8081:80`;
  - `http://localhost:8081` → Nginx внутри кластера.

**Цепочка трафика:**

- `browser → localhost:8081 → port-forward → Service demo-nginx → Pods (nginx:alpine)`.

### 5. Docker Desktop GUI

**Images:**
- вкладка `Images`:
  - `devops-nginx:latest`, `ci-demo-app:latest` — твои образы;
  - образы Kubernetes (`docker-desktop-kubernetes`, `kube-*`) — служебные.

**Containers:**
- вкладка `Containers`:
  - обычные контейнеры (например, `devops-nginx` с портом `8080:80`);
  - Kubernetes-контейнеры с префиксом `k8s_...` (Pods).
- из GUI можно:
  - смотреть логи;
  - видеть проброс портов;
  - останавливать/удалять контейнеры.

### 6. Мониторинг и логирование (концептуально)

- **Prometheus**:
  - собирает метрики с сервисов и кластера по HTTP (`/metrics`);
  - хранит временные ряды;
  - на основе правил алертинга (через Alertmanager) шлёт уведомления.
- **Grafana**:
  - строит дашборды по данным из Prometheus и других источников;
  - даёт быстрый обзор: нагрузка, ошибки, задержки, состояние сервисов.

В связке с Kubernetes:
- метрики по нодам/Pod-ам (CPU, память, рестарты, ошибки);
- бизнес-метрики приложений (запросы, ошибки, latency);
- алерты при отклонениях.


