## Практика 02 — Laravel + Docker + CI + Kubernetes + Helm + Monitoring

Здесь будет «боевой» учебный проект, максимально похожий на вакансию:

- Laravel-приложение;
- окружение на Docker/docker-compose (PHP-FPM + Nginx + DB + Redis);
- CI (GitHub Actions) для Laravel;
- манифесты Kubernetes + Helm-чарт;
- базовый мониторинг (Prometheus + Grafana) в кластере Docker Desktop.

### 1. Структура директории

Планируемая структура:

- `laravel-app/`
  - `src/` — исходники Laravel-приложения (создадим через `composer create-project`).
  - `docker/`
    - `php-fpm/Dockerfile`
    - `nginx/Dockerfile`
    - `nginx/nginx.conf`
  - `docker-compose.yml` — локальное окружение (app + nginx + db + redis).
  - `k8s/` — манифесты Kubernetes.
  - `helm/laravel-app/` — Helm-чарт.
  - `.github/workflows/laravel-ci.yml` — CI под Laravel.
  - `README-laravel-devops.md` — общее описание (этот файл).

### 2. Создание Laravel-приложения (в Ubuntu/WSL)

В Ubuntu:

```bash
cd /mnt/d/DevOpsPractice/laravel-app

# 1. Установить composer (если ещё нет)
# см. официальный сайт getcomposer.org — можно поставить глобально в WSL

# 2. Создать проект Laravel в папке src
composer create-project laravel/laravel src

cd src
cp .env.example .env
php artisan key:generate
```

На этом этапе:
- Laravel запускается через встроенный `php artisan serve` (по желанию);
- дальше мы будем заворачивать его в Docker.

#### Настройка `.env` под docker-compose

В `src/.env` нужно будет выставить значения, согласованные с `docker-compose.yml`:

```env
APP_URL=http://localhost:8082

DB_CONNECTION=mysql
DB_HOST=db
DB_PORT=3306
DB_DATABASE=laravel
DB_USERNAME=laravel
DB_PASSWORD=secret

REDIS_HOST=redis
REDIS_PASSWORD=null
REDIS_PORT=6379

QUEUE_CONNECTION=redis
CACHE_STORE=redis
```

### 3. Docker + docker-compose

Мы создадим:

- `docker/php-fpm/Dockerfile` — образ с PHP-FPM и зависимостями (pdo, redis и т.п.).
- `docker/nginx/Dockerfile` + `docker/nginx/nginx.conf` — фронтовый Nginx.
- `docker-compose.yml`:
  - сервис `app` (php-fpm + Laravel);
  - сервис `nginx` (прокси на `app`);
  - сервис `db` (MySQL/PostgreSQL);
  - сервис `redis`.

Запуск будет выглядеть примерно так:

```bash
cd /mnt/d/DevOpsPractice/laravel-app
docker compose up --build
```

После этого Laravel должен открываться в браузере (например, на `http://localhost:8082`).

### 4. Дальше по плану

В следующих шагах мы:

1. Добавим **CI для Laravel** (GitHub Actions):
   - `composer install`;
   - `php artisan test`;
   - сборка Docker-образа.
2. Описанием окружение в **Kubernetes** (web + queue worker + redis + db).
3. Оформим это в **Helm-чарт** с `values.yaml`.
4. Поднимем **Prometheus + Grafana** в кластере Docker Desktop (через Helm) и посмотрим базовые метрики.

Все шаги будем делать по очереди, с подробными комментариями, как сегодня в первой практике.


