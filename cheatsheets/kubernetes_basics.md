## Kubernetes — базовая шпаргалка под собес

Мы используем мини-проект в папке `k8s-demo`:

- `deployment.yaml` — Deployment с Nginx + env из ConfigMap/Secret;
- `service.yaml` — Service для доступа к подам;
- `ingress.yaml` — Ingress, который ведёт трафик на Service;
- `configmap.yaml` — не секретные настройки;
- `secret.yaml` — секреты (в base64).

### 1. Общая картина (что нужно уметь объяснить)

- **Pod** — минимальная единица запуска в Kubernetes:
  - содержит один или несколько контейнеров;
  - разделяют сеть и диск внутри Pod-а.
- **Deployment** — контроллер, который управляет Pod-ами:
  - следит, чтобы работало нужное количество реплик;
  - обновляет Pod-ы «по очереди» (rolling update).
- **Service** — стабильная точка входа к Pod-ам:
  - даёт постоянное имя и IP;
  - распределяет трафик по Pod-ам (через selector-ы по label-ам).
- **Ingress** — входной HTTP(S) трафик снаружи в кластер:
  - работает поверх Ingress Controller (часто Nginx);
  - по хосту/пути решает, в какой Service направить запрос.
- **ConfigMap** — конфиги (не секретные):
  - хранит пары ключ/значение (строки);
  - удобно для env-переменных, конфигов приложений.
- **Secret** — конфиги с секретами:
  - тоже ключ/значение, но данные хранятся в base64;
  - пароли, токены, ключи.

### 2. Deployment (`k8s-demo/deployment.yaml`)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: demo-nginx
  labels:
    app: demo-nginx
spec:
  replicas: 2
  selector:
    matchLabels:
      app: demo-nginx
  template:
    metadata:
      labels:
        app: demo-nginx
    spec:
      containers:
        - name: nginx
          image: nginx:alpine
          ports:
            - containerPort: 80
          env:
            - name: APP_ENV
              valueFrom:
                configMapKeyRef:
                  name: demo-config
                  key: APP_ENV
            - name: APP_SECRET
              valueFrom:
                secretKeyRef:
                  name: demo-secret
                  key: APP_SECRET
```

Ключевые моменты:
- **`replicas: 2`** — хотим 2 копии Pod-а (2 экземпляра Nginx).
- **`selector.matchLabels`** и `template.metadata.labels`:
  - Deployment управляет Pod-ами, у которых `app: demo-nginx`;
  - важно, чтобы selector и labels совпадали.
- Внутри `spec.template.spec.containers`:
  - **`image: nginx:alpine`** — будем запускать официальный Nginx;
  - **`containerPort: 80`** — контейнер слушает порт 80.
- Блок `env`:
  - `APP_ENV` приходит из **ConfigMap** `demo-config` (ключ `APP_ENV`);
  - `APP_SECRET` приходит из **Secret** `demo-secret` (ключ `APP_SECRET`).

В реальном кластере мы бы применили это так:

```bash
kubectl apply -f deployment.yaml
kubectl get deployments
kubectl get pods -l app=demo-nginx
```

### 3. Service (`k8s-demo/service.yaml`)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: demo-nginx
  labels:
    app: demo-nginx
spec:
  type: ClusterIP
  selector:
    app: demo-nginx
  ports:
    - port: 80
      targetPort: 80
```

Разбор:
- **`type: ClusterIP`** — Service доступен только внутри кластера:
  - другие Pod-ы могут ходить к нему по `demo-nginx:80`;
  - для внешнего мира нужен ещё Ingress или тип `LoadBalancer`/`NodePort`.
- **`selector.app: demo-nginx`** — Service отправляет трафик на Pod-ы с таким label.
- **`port` vs `targetPort`**:
  - `port: 80` — порт самого Service;
  - `targetPort: 80` — куда Service отправляет запрос внутри Pod-а (на `containerPort` контейнера).

Пример применения:

```bash
kubectl apply -f service.yaml
kubectl get svc demo-nginx
```

### 4. Ingress (`k8s-demo/ingress.yaml`)

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: demo-nginx
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
    - host: demo.local
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: demo-nginx
                port:
                  number: 80
```

Идея:
- Ingress принимает HTTP-запросы на хост `demo.local` и путь `/`;
- затем перенаправляет их в Service `demo-nginx:80`.

Важно:
- Ingress сам по себе не работает без **Ingress Controller** (обычно это Nginx Ingress Controller или другой);
- аннотация `nginx.ingress.kubernetes.io/rewrite-target` управляет тем, как Nginx обрабатывает путь (для простоты сейчас можно просто знать, что это спец-настройка для Nginx-контроллера).

### 5. ConfigMap (`k8s-demo/configmap.yaml`)

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: demo-config
data:
  APP_ENV: "production"
```

- Хранит не секретные настройки.
- Поле `data` — ключ/значение (всегда строки).
- В нашем Deployment-е переменная окружения `APP_ENV` читается из этого ConfigMap.

Применение в реальном кластере:

```bash
kubectl apply -f configmap.yaml
kubectl get configmap demo-config -o yaml
```

### 6. Secret (`k8s-demo/secret.yaml`)

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: demo-secret
type: Opaque
data:
  APP_SECRET: c3VwZXItc2VjcmV0LXRva2Vu
```

Особенности:
- **`type: Opaque`** — обычный произвольный секрет (самый частый тип).
- В `data` значения указываются в **base64**.
  - Пример: строка `super-secret-token` закодирована в base64 как `c3VwZXItc2VjcmV0LXRva2Vu`.

Проверка кодирования (в Linux):

```bash
echo -n "super-secret-token" | base64
echo -n "c3VwZXItc2VjcmV0LXRva2Vu" | base64 --decode
```

В нашем Deployment-е переменная `APP_SECRET` берётся именно из этого Secret.

### 7. Типовые команды `kubectl` (на уровне теории)

Даже если мы не успеем поднять кластер локально, важно знать базовые команды:

```bash
kubectl apply -f deployment.yaml          # создать/обновить Deployment
kubectl delete -f deployment.yaml         # удалить ресурсы из файла

kubectl get pods                          # список Pod-ов
kubectl get pods -o wide                  # с дополнительной информацией
kubectl get svc                           # список Service-ов
kubectl get ingress                       # список Ingress-ов

kubectl describe pod <имя-pod>            # подробная инфа и события по Pod-у
kubectl logs <имя-pod>                    # логи с контейнера в Pod-е
kubectl logs -f <имя-pod>                 # «фолловить» логи (stream)
```

### 8. Фразы для собеса по Kubernetes

- «Понимаю базовые объекты Kubernetes: Pod, Deployment, Service, Ingress, ConfigMap, Secret.»
- «Могу написать простой Deployment с несколькими репликами, Service для доступа к Pod-ам и Ingress, который прокидывает HTTP-трафик снаружи на Service.»
- «Знаю, как использовать ConfigMap и Secret для передачи конфигурации и секретов в контейнеры через переменные окружения.»
- «Работал с `kubectl apply -f ...`, `kubectl get`, `kubectl describe`, `kubectl logs` на уровне учебных примеров.»

---

### 9. Kubernetes «на пальцах», на примере того, что ты только что сделал

Представь историю шаг за шагом.

#### Шаг 1. Разработчик собирает Docker-образ

- Сначала есть **код приложения** (например, Laravel или наш Nginx с `index.html`).
- Для него пишут **`Dockerfile`** и собирают образ:

```bash
docker build -t my-app .
```

- Получается **image** — «упакованное приложение» (файлы + зависимости).

В нашем случае:
- мы собирали образ `devops-nginx` (локально);
- в Kubernetes-примере для простоты используем уже готовый образ `nginx:alpine`.

#### Шаг 2. Образ попадает в кластер

Обычно:
- образ отправляют в **registry** (Docker Hub, GitLab Registry и т.п.);
- Kubernetes вытаскивает образ из registry, когда создаёт Pod.

У нас:
- кластер Docker Desktop и Docker-демон — на одной машине;
- образ `nginx:alpine` скачивается из Docker Hub **прямо из кластера**.

#### Шаг 3. Deployment говорит: «хочу 2 копии приложения»

В `deployment.yaml` ты описал желание:

```yaml
kind: Deployment
spec:
  replicas: 2
  template:
    spec:
      containers:
        - name: nginx
          image: nginx:alpine
```

Смысл:
- «Kubernetes, пожалуйста, **держи запущенными 2 Pod-а** с контейнером на образе `nginx:alpine`. Если что-то упадёт — перезапусти.»

Контроллер Deployment:
- создаёт нужное количество Pod-ов;
- следит, чтобы их всегда было `replicas` штук.

Ты это видишь так:

```bash
kubectl get deployments
kubectl get pods
```

И в GUI Docker Desktop — Deployment `demo-nginx` и 2 Pod-а.

#### Шаг 4. Service даёт стабильный адрес к этим Pod-ам

Проблема:
- Pod-ы могут пересоздаваться → их IP меняются;
- напрямую ходить на Pod-IP неудобно.

Решение — **Service**:

```yaml
kind: Service
spec:
  type: ClusterIP
  selector:
    app: demo-nginx
  ports:
    - port: 80
      targetPort: 80
```

Смысл:
- «Создай внутри кластера **виртуальный IP** (ClusterIP), который называется `demo-nginx:80`, и всё, что приходит на него, **раскидывай по Pod-ам**, у которых label `app: demo-nginx`.»

В результате:
- другие сервисы в кластере могут обращаться к нашему приложению как к `http://demo-nginx:80`;
- трафик будет балансироваться между двумя Pod-ами.

#### Шаг 5. Ingress впускает HTTP-трафик снаружи

Снаружи кластера пользователей интересует **HTTP по доменному имени**.

Ingress:

```yaml
kind: Ingress
spec:
  rules:
    - host: demo.local
      http:
        paths:
          - path: /
            backend:
              service:
                name: demo-nginx
                port:
                  number: 80
```

Смысл:
- «Когда приходит HTTP-запрос на `demo.local/`, отправь его в Service `demo-nginx:80`.»

Если установлен Nginx Ingress Controller, он:
- слушает HTTP/HTTPS снаружи;
- смотрит на `Host` и `path` запроса;
- решает, в какой Service внутри кластера отправить запрос.

Так выстраивается цепочка:

> Браузер → Ingress (Nginx controller) → Service `demo-nginx` → Pods (Nginx контейнеры внутри Deployment).

#### Шаг 6. Где тут Docker

- **Внутри Pod-ов** у тебя крутятся **Docker-контейнеры** (в Docker Desktop это прям один и тот же движок).
- Kubernetes:
  - не сам запускает контейнеры, а говорит: «runtime, запусти мне контейнер с таким образом»;
  - в Docker Desktop этим runtime является Docker.
- То есть:
  - Docker отвечает за **упаковку и запуск контейнеров**;
  - Kubernetes отвечает за **оркестрацию**: сколько контейнеров, где, как к ним ходить, как обновлять.

Можно так сформулировать:
- Docker — это **про один контейнер** (или пару) на одной машине;
- Kubernetes — это **про много контейнеров** на кластере машин, + сам себя лечит, балансирует трафик и т.п.



