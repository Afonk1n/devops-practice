# Инструкция по развёртыванию Laravel-приложения в Kubernetes

Эта инструкция поможет развернуть Laravel-приложение в Kubernetes-кластере (Docker Desktop) с использованием Helm.

## Предварительные требования

1. **Docker Desktop** установлен и запущен
2. **Kubernetes** включён в Docker Desktop (Settings → Kubernetes → Enable Kubernetes)
3. **Helm 3.x** установлен (проверка: `helm version`)
4. **WSL2 + Ubuntu** (для Windows) или Linux-терминал

### Проверка окружения

```bash
# Проверить Docker
docker --version

# Проверить Kubernetes
kubectl version --client
kubectl get nodes

# Проверить Helm
helm version
```

Если что-то не работает — установи недостающие компоненты.

---

## Шаг 1: Сборка Docker-образов

Перейди в папку проекта и собери образы для PHP-FPM и Nginx:

```bash
cd /mnt/d/DevOpsPractice/laravel-app

# Собрать образ PHP-FPM (с кодом Laravel)
sudo docker build -f docker/php-fpm/Dockerfile.k8s -t laravel-app-app:latest .

# Собрать образ Nginx
sudo docker build -f docker/nginx/Dockerfile.k8s -t laravel-app-nginx:latest .
```

**Что происходит:**
- `Dockerfile.k8s` копирует код Laravel в образ и устанавливает зависимости через `composer install`
- Образы получают теги `laravel-app-app:latest` и `laravel-app-nginx:latest`
- Эти имена должны совпадать с `values.yaml` в Helm-чарте

**Проверка:**
```bash
docker images | grep laravel-app
```

Должны быть два образа: `laravel-app-app` и `laravel-app-nginx`.

---

## Шаг 2: Установка через Helm

Установи приложение в Kubernetes через Helm-чарт:

```bash
cd /mnt/d/DevOpsPractice/laravel-app/helm/laravel-app

# Проверить шаблоны (опционально, для отладки)
helm template laravel-app . --debug

# Установить приложение
helm install laravel-app .
```

**Что происходит:**
- Helm читает `Chart.yaml` и `values.yaml`
- Генерирует Kubernetes-манифесты из шаблонов в `templates/`
- Применяет их в кластер (создаёт Deployment, Service, ConfigMap, Secret и т.д.)

**Проверка установки:**
```bash
# Проверить статус Helm-релиза
helm status laravel-app

# Проверить поды
kubectl get pods

# Должны быть поды:
# - laravel-app-web-xxx (2/2 Running) - Laravel приложение
# - laravel-app-mysql-xxx (1/1 Running) - MySQL
# - laravel-app-redis-xxx (1/1 Running) - Redis
```

**Если поды не запускаются:**
```bash
# Посмотреть события
kubectl get events --sort-by='.lastTimestamp'

# Посмотреть логи пода
kubectl logs <pod-name> -c app  # для контейнера app
kubectl logs <pod-name> -c nginx  # для контейнера nginx

# Описание пода (для диагностики)
kubectl describe pod <pod-name>
```

---

## Шаг 3: Выполнение миграций базы данных

После того как поды запустились, нужно выполнить миграции Laravel:

```bash
# Найти имя пода Laravel
kubectl get pods -l app.kubernetes.io/name=laravel-app

# Выполнить миграции (замени <pod-name> на реальное имя)
kubectl exec -it <pod-name> -c app -- php artisan migrate --force
```

**Или автоматически найти под:**
```bash
POD_NAME=$(kubectl get pods -l app.kubernetes.io/name=laravel-app -o jsonpath='{.items[0].metadata.name}')
kubectl exec -it $POD_NAME -c app -- php artisan migrate --force
```

**Что происходит:**
- `php artisan migrate --force` создаёт таблицы в базе данных MySQL
- Флаг `--force` нужен, потому что мы в production-окружении

**Проверка:**
```bash
# Проверить, что миграции выполнены
kubectl exec -it $POD_NAME -c app -- php artisan migrate:status
```

---

## Шаг 4: Проверка работы приложения

### Вариант 1: Через port-forward (для локального доступа)

```bash
# Пробросить порт Service в локальную машину
kubectl port-forward service/laravel-app-web 8080:80
```

Затем открой в браузере: `http://localhost:8080`

**Должна открыться стартовая страница Laravel.**

### Вариант 2: Через Ingress (если настроен Ingress Controller)

Если у тебя установлен Ingress Controller (например, Nginx Ingress), приложение будет доступно по адресу из `ingress.yaml` (по умолчанию `laravel-app.local`).

Добавь в `/etc/hosts` (Linux/Mac) или `C:\Windows\System32\drivers\etc\hosts` (Windows):
```
127.0.0.1 laravel-app.local
```

Затем открой в браузере: `http://laravel-app.local`

---

## Шаг 5: Полезные команды для управления

### Обновление приложения

```bash
# Обновить с новыми значениями
helm upgrade laravel-app . --set app.replicas=2

# Обновить с кастомным файлом values
helm upgrade laravel-app . -f my-values.yaml
```

### Масштабирование

```bash
# Увеличить количество реплик до 2
helm upgrade laravel-app . --set app.replicas=2

# Проверить поды (должно быть 2 пода)
kubectl get pods -l app.kubernetes.io/name=laravel-app
```

### Просмотр логов

```bash
# Логи контейнера app (PHP-FPM)
kubectl logs <pod-name> -c app

# Логи контейнера nginx
kubectl logs <pod-name> -c nginx

# Логи с отслеживанием (как tail -f)
kubectl logs -f <pod-name> -c app
```

### Выполнение команд в контейнере

```bash
# Запустить tinker (интерактивная консоль Laravel)
kubectl exec -it <pod-name> -c app -- php artisan tinker

# Очистить кеш
kubectl exec -it <pod-name> -c app -- php artisan cache:clear
kubectl exec -it <pod-name> -c app -- php artisan config:clear

# Проверить переменные окружения
kubectl exec -it <pod-name> -c app -- env | grep APP_
```

### Проверка состояния

```bash
# Статус Helm-релиза
helm status laravel-app

# Все ресурсы
kubectl get all

# Сервисы
kubectl get svc

# ConfigMap и Secret
kubectl get configmap
kubectl get secret

# NetworkPolicy
kubectl get networkpolicy
```

---

## Шаг 6: Удаление приложения

Если нужно удалить всё приложение:

```bash
# Удалить Helm-релиз (удалит все ресурсы)
helm uninstall laravel-app

# Проверить, что всё удалено
kubectl get pods
kubectl get svc
```

---

## Возможные проблемы и решения

### Проблема: Поды не запускаются (CrashLoopBackOff)

**Решение:**
```bash
# Посмотреть логи
kubectl logs <pod-name> -c app

# Посмотреть события
kubectl describe pod <pod-name>

# Частые причины:
# - Не собран Docker-образ (выполни Шаг 1)
# - Неправильные переменные окружения (проверь ConfigMap/Secret)
# - Проблемы с подключением к базе (проверь, что MySQL под запущен)
```

### Проблема: "No application encryption key has been specified"

**Решение:**
```bash
# Проверить, что APP_KEY есть в ConfigMap
kubectl get configmap laravel-app-config -o yaml | grep APP_KEY

# Если нет — добавить в values.yaml и обновить
helm upgrade laravel-app . --set laravel.appKey="base64:ТВОЙ_КЛЮЧ"
```

### Проблема: "Connection refused" к MySQL

**Решение:**
```bash
# Проверить, что MySQL под запущен
kubectl get pods | grep mysql

# Проверить Service
kubectl get svc | grep mysql

# Проверить переменные окружения в Laravel-поде
kubectl exec -it <pod-name> -c app -- env | grep DB_
```

### Проблема: Health checks не проходят

**Решение:**
```bash
# Проверить probes в Deployment
kubectl describe pod <pod-name> | grep -A 5 "Liveness\|Readiness"

# Если используется tcpSocket на порту 9000, убедись, что PHP-FPM слушает этот порт
kubectl exec -it <pod-name> -c app -- netstat -tlnp | grep 9000
```

---

## Структура проекта

```
laravel-app/
├── docker/                    # Dockerfile'ы
│   ├── php-fpm/
│   │   ├── Dockerfile         # Для docker-compose
│   │   └── Dockerfile.k8s     # Для Kubernetes (с кодом)
│   └── nginx/
│       ├── Dockerfile         # Для docker-compose
│       ├── Dockerfile.k8s     # Для Kubernetes (с кодом)
│       └── nginx.conf         # Конфигурация Nginx
├── helm/laravel-app/          # Helm-чарт
│   ├── Chart.yaml            # Метаданные чарта
│   ├── values.yaml            # Настройки по умолчанию
│   └── templates/             # Шаблоны Kubernetes-манифестов
├── k8s/                       # Исходные манифесты (для наглядности)
├── src/                       # Код Laravel-приложения
└── docker-compose.yml         # Для локальной разработки
```

---

## Дополнительно

### Локальная разработка (docker-compose)

Для локальной разработки можно использовать docker-compose:

```bash
cd /mnt/d/DevOpsPractice/laravel-app
docker compose up --build
```

Приложение будет доступно на `http://localhost:8082`

### Мониторинг (Prometheus + Grafana)

Если нужно установить мониторинг:

```bash
# Добавить репозиторий
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Установить
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace

# Получить пароль Grafana
kubectl get secret prometheus-grafana -n monitoring \
  -o jsonpath="{.data.admin-password}" | base64 -d

# Доступ к Grafana
kubectl port-forward -n monitoring service/prometheus-grafana 3000:80
```

Открой `http://localhost:3000`, логин: `admin`, пароль: (из команды выше)

---

## Итог

После выполнения всех шагов у тебя будет:
- ✅ Laravel-приложение работает в Kubernetes
- ✅ MySQL и Redis развёрнуты как отдельные сервисы
- ✅ Приложение доступно через port-forward или Ingress
- ✅ Health checks настроены
- ✅ NetworkPolicy ограничивает сетевой трафик
- ✅ Всё управляется через Helm

**Проверка финального состояния:**
```bash
helm status laravel-app
kubectl get pods
kubectl get svc
```

Все поды должны быть в статусе `Running`, сервисы — `ClusterIP`.

