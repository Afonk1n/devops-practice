# Пошаговая инструкция по развёртыванию Laravel-приложения

Полная инструкция от установки WSL до запуска мониторинга.

---

## Шаг 0: Установка WSL2 + Ubuntu (только для Windows)

**Если у тебя уже есть WSL2 и Ubuntu — пропусти этот шаг.**

1. **Установить WSL2:**
   ```powershell
   # В PowerShell от администратора
   wsl --install
   ```
   Перезагрузи компьютер.

2. **Установить Ubuntu:**
   - После перезагрузки открой Ubuntu из меню Пуск
   - Создай пользователя (имя и пароль)

3. **Проверка:**
   ```bash
   # В Ubuntu
   wsl --version
   ```

---

## Шаг 1: Установка Docker Desktop

1. **Скачать Docker Desktop:**
   - https://www.docker.com/products/docker-desktop/
   - Установи и запусти

2. **Включить Kubernetes:**
   - Docker Desktop → Settings → Kubernetes
   - Поставь галочку "Enable Kubernetes"
   - Нажми "Apply & Restart"

3. **Проверка:**
   ```bash
   # В WSL (Ubuntu)
   docker --version
   kubectl version --client
   kubectl get nodes
   ```
   Должен быть один узел в статусе `Ready`.

---

## Шаг 2: Установка Helm

```bash
# В WSL (Ubuntu)
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

**Проверка:**
```bash
helm version
```

Должна быть версия Helm 3.x.

---

## Шаг 3: Клонирование репозитория

```bash
# В WSL (Ubuntu)
cd ~
git clone https://github.com/Afonk1n/devops-practice.git
cd devops-practice/laravel-app
```

**Проверка:**
```bash
ls -la
# Должны быть папки: docker/, helm/, k8s/, src/
```

---

## Шаг 4: Сборка Docker-образов

```bash
# В WSL, в папке laravel-app
cd ~/devops-practice/laravel-app

# Собрать образ PHP-FPM
sudo docker build -f docker/php-fpm/Dockerfile.k8s -t laravel-app-app:latest .

# Собрать образ Nginx
sudo docker build -f docker/nginx/Dockerfile.k8s -t laravel-app-nginx:latest .
```

**Проверка:**
```bash
docker images | grep laravel-app
```

Должны быть два образа: `laravel-app-app` и `laravel-app-nginx`.

**Время:** ~2-5 минут (зависит от скорости интернета).

---

## Шаг 5: Установка приложения через Helm

```bash
# Перейти в папку Helm-чарта
cd ~/devops-practice/laravel-app/helm/laravel-app

# Установить приложение
helm install laravel-app .
```

**Проверка:**
```bash
# Статус установки
helm status laravel-app

# Проверить поды (подожди 30-60 секунд, пока запустятся)
kubectl get pods

# Должны быть:
# - laravel-app-web-xxx (2/2 Running)
# - laravel-app-mysql-xxx (1/1 Running)
# - laravel-app-redis-xxx (1/1 Running)
```

**Если поды не запускаются:**
```bash
# Посмотреть логи
kubectl logs <pod-name> -c app
kubectl describe pod <pod-name>
```

---

## Шаг 6: Выполнение миграций базы данных

```bash
# Найти имя пода Laravel
POD_NAME=$(kubectl get pods -l app.kubernetes.io/name=laravel-app -o jsonpath='{.items[0].metadata.name}')

# Выполнить миграции
kubectl exec -it $POD_NAME -c app -- php artisan migrate --force
```

**Проверка:**
```bash
# Проверить статус миграций
kubectl exec -it $POD_NAME -c app -- php artisan migrate:status
```

Должны быть выполнены все миграции.

---

## Шаг 7: Проверка работы приложения

```bash
# Пробросить порт в локальную машину
kubectl port-forward service/laravel-app-web 8080:80
```

**Открой в браузере:** `http://localhost:8080`

**Должна открыться стартовая страница Laravel.**

**Чтобы остановить port-forward:** нажми `Ctrl+C` в терминале.

---

## Шаг 8: Установка мониторинга (Prometheus + Grafana)

### 8.1. Добавить репозиторий Helm

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
```

**Проверка:**
```bash
helm repo list
```

Должен быть репозиторий `prometheus-community`.

### 8.2. Установить kube-prometheus-stack

```bash
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace
```

**Проверка:**
```bash
# Подожди 1-2 минуты, пока запустятся поды
kubectl get pods -n monitoring

# Должны быть поды:
# - prometheus-grafana-xxx (3/3 Running)
# - prometheus-kube-prometheus-operator-xxx (1/1 Running)
# - prometheus-kube-state-metrics-xxx (1/1 Running)
# - prometheus-prometheus-kube-prometheus-prometheus-0 (2/2 Running)
# - alertmanager-prometheus-kube-prometheus-alertmanager-0 (2/2 Running)
```

**Время:** ~2-3 минуты на запуск всех подов.

### 8.3. Получить пароль Grafana

```bash
kubectl get secret prometheus-grafana -n monitoring \
  -o jsonpath="{.data.admin-password}" | base64 -d
```

**Скопируй пароль** (он понадобится для входа).

### 8.4. Доступ к Grafana

```bash
# Пробросить порт Grafana
kubectl port-forward -n monitoring service/prometheus-grafana 3000:80
```

**Открой в браузере:** `http://localhost:3000`

**Логин:** `admin`  
**Пароль:** (тот, что скопировал в шаге 8.3)

### 8.5. Просмотр дашбордов в Grafana

После входа в Grafana:

1. **Найди готовые дашборды:**
   - Слева меню → Dashboards → Browse
   - Или в поиске: "Kubernetes", "Node", "Pod"

2. **Популярные дашборды:**
   - "Kubernetes / Compute Resources / Pod"
   - "Node Exporter / Nodes"
   - "Kubernetes / Kubelet"

3. **Посмотреть метрики Laravel-приложения:**
   - Выбери дашборд "Kubernetes / Compute Resources / Pod"
   - В фильтре выбери namespace: `default`
   - Выбери под: `laravel-app-web-xxx`
   - Увидишь CPU, память, сеть для твоего приложения

**Чтобы остановить port-forward:** нажми `Ctrl+C` в терминале.

---

## Шаг 9: Итоговая проверка

```bash
# Проверить все поды
kubectl get pods

# Проверить сервисы
kubectl get svc

# Проверить Helm-релизы
helm list

# Проверить мониторинг
kubectl get pods -n monitoring
```

**Должно быть:**
- ✅ Все поды в статусе `Running`
- ✅ Сервисы в статусе `ClusterIP`
- ✅ Helm-релизы: `laravel-app` и `prometheus`
- ✅ Мониторинг работает (поды в namespace `monitoring`)

---

## Полезные команды

### Просмотр логов

```bash
# Логи Laravel-приложения
POD_NAME=$(kubectl get pods -l app.kubernetes.io/name=laravel-app -o jsonpath='{.items[0].metadata.name}')
kubectl logs $POD_NAME -c app
kubectl logs $POD_NAME -c nginx

# Логи с отслеживанием (как tail -f)
kubectl logs -f $POD_NAME -c app
```

### Масштабирование

```bash
# Увеличить количество реплик до 2
cd ~/devops-practice/laravel-app/helm/laravel-app
helm upgrade laravel-app . --set app.replicas=2

# Проверить
kubectl get pods -l app.kubernetes.io/name=laravel-app
```

### Выполнение команд в контейнере

```bash
# Очистить кеш Laravel
kubectl exec -it $POD_NAME -c app -- php artisan cache:clear

# Проверить переменные окружения
kubectl exec -it $POD_NAME -c app -- env | grep APP_
```

### Удаление приложения

```bash
# Удалить Laravel-приложение
helm uninstall laravel-app

# Удалить мониторинг
helm uninstall prometheus -n monitoring
```

---

## Возможные проблемы

### Проблема: "permission denied" при docker build

**Решение:**
```bash
# Использовать sudo
sudo docker build -f docker/php-fpm/Dockerfile.k8s -t laravel-app-app:latest .
```

### Проблема: Поды не запускаются (CrashLoopBackOff)

**Решение:**
```bash
# Посмотреть логи
kubectl logs <pod-name> -c app
kubectl describe pod <pod-name>

# Частые причины:
# - Не собран Docker-образ (выполни Шаг 4)
# - MySQL не запустился (подожди ещё минуту)
```

### Проблема: "No application encryption key"

**Решение:**
```bash
# Проверить ConfigMap
kubectl get configmap laravel-app-config -o yaml | grep APP_KEY

# Если пусто — обновить через Helm
cd ~/devops-practice/laravel-app/helm/laravel-app
helm upgrade laravel-app . --set laravel.appKey="base64:ТВОЙ_КЛЮЧ"
```

### Проблема: Grafana показывает "No data"

**Решение:**
- Это нормально для Docker Desktop (ограниченные метрики)
- Попробуй другие дашборды или подожди 5-10 минут
- В реальном кластере метрики будут работать лучше

---

## Итог

После выполнения всех шагов у тебя будет:

- ✅ WSL2 + Ubuntu установлены
- ✅ Docker Desktop с Kubernetes работает
- ✅ Helm установлен
- ✅ Laravel-приложение работает в Kubernetes
- ✅ MySQL и Redis развёрнуты
- ✅ Приложение доступно на `http://localhost:8080`
- ✅ Мониторинг установлен (Prometheus + Grafana)
- ✅ Grafana доступна на `http://localhost:3000`

**Время выполнения:** ~30-40 минут (включая установку и ожидание запуска подов).

---

## Структура проекта

```
devops-practice/
├── DEPLOYMENT.md              # Эта инструкция
├── final_overview_laravel.md  # Подробная документация
├── interview_script_laravel.md # Речевые формулировки
└── laravel-app/
    ├── docker/                # Dockerfile'ы
    ├── helm/laravel-app/      # Helm-чарт
    ├── k8s/                   # Манифесты (для наглядности)
    └── src/                   # Код Laravel
```

---

**Готово!** Проект полностью развёрнут и готов к работе.
