## CI/CD — минимальная шпаргалка (на примере GitHub Actions)

### 1. Основные понятия

- **CI (Continuous Integration)** — каждый пуш/merge в репозиторий:
  - запускает **автоматические проверки** (сборка, тесты, линтеры);
  - цель — сломанный код не попадает в main.
- **CD (Continuous Delivery / Deployment)**:
  - Delivery — всё готово к деплою, но требует ручного подтверждения;
  - Deployment — код **автоматически** выкатывается на среду (staging/prod).

В инструментах типа GitHub Actions / GitLab CI всё это описывается в YAML:
- **pipeline** (workflow) → из каких **jobs** и **steps** состоит;
- на какие события реагирует (`on: push`, `on: pull_request` и т.п.).

### 2. Наш пример workflow (`.github/workflows/docker-ci.yml`)

```yaml
name: CI for Simple Docker App

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
```

- **`name`** — просто человекочитаемое имя пайплайна.
- **`on`** — на какие события триггерится:
  - `push` в ветку `main`;
  - `pull_request` в ветку `main`.

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
```

- **`jobs`** — набор задач, которые можно запускать параллельно или последовательно.
- Здесь одна job: **`build`**.
- **`runs-on: ubuntu-latest`** — GitHub Actions поднимет виртуалку с Ubuntu, в которой выполнятся все шаги этой job.

```yaml
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
```

- **`steps`** — конкретные шаги внутри job.
- Шаг `Checkout repository`:
  - `uses: actions/checkout@v4` — стандартный action от GitHub;
  - подтягивает код репозитория в файловую систему runner-а.

```yaml
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
```

- Настройка окружения Docker Buildx для сборки образов.

```yaml
      - name: Build Docker image
        uses: docker/build-push-action@v6
        with:
          context: ./simple-app
          push: false
          tags: ci-demo-app:latest
```

- Шаг, который **собирает Docker-образ**:
  - **`uses: docker/build-push-action@v6`** — официальный action от Docker;
  - **`context: ./simple-app`** — папка с `Dockerfile` и кодом;
  - **`push: false`** — только собираем образ, не пушим в registry;
  - **`tags: ci-demo-app:latest`** — имя и тег собираемого образа.

То есть весь workflow делает следующее:
- при каждом `push`/`pull_request` в `main`:
  1. берёт код репозитория;
  2. находит `simple-app/Dockerfile`;
  3. пробует собрать Docker-образ.

Если сборка падает → CI красный, менять код/`Dockerfile` до исправления.

### 3. Как это «звучит» на собесе

- «Работал с CI на уровне GitHub Actions: описывал простой workflow, который на каждый push собирает Docker-образ приложения.»
- «Понимаю базовую структуру пайплайна: `on` — события, `jobs` — задачи, `steps` — шаги внутри job. Использовал стандартные экшены типа `actions/checkout`, `docker/build-push-action`.»
- «Вижу, как CI вписывается в DevOps-цепочку: разработчик пушит код → CI собирает и проверяет образ → дальше можно либо вручную, либо автоматически деплоить в Kubernetes.»


