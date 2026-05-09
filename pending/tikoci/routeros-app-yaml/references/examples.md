# RouterOS /app YAML — Reference Examples

## Minimal /app

```yaml
name: hello-nginx
services:
  web:
    image: nginx:alpine
    ports:
      - "8080:80/tcp"
```

## Full-Featured /app (All Properties)

```yaml
name: my-app
descr: A full-featured example app
page: https://example.com/my-app
category: productivity
icon: https://example.com/icon.png
default-credentials: admin:admin
url-path: /dashboard
auto-update: true

services:
  web:
    image: ghcr.io/owner/web-app:latest
    container_name: my-web
    hostname: web
    entrypoint: ["/bin/sh", "-c"]
    command: "nginx -g 'daemon off;'"
    ports:
      - "[accessIP]:[accessPort]:80:web:tcp"
      - "8443:443/tcp:https"
      - target: 9090
        published: 9090
        protocol: tcp
        name: metrics
        app_protocol: http
    environment:
      APP_HOST: "[accessIP]"
      APP_PORT: "[accessPort]"
      DB_HOST: "[containerIP]"
      ROUTER_IP: "[routerIP]"
    volumes:
      - web-data:/var/www/html
    configs:
      - source: nginx-conf
        target: /etc/nginx/nginx.conf
        mode: 0644
    restart: unless-stopped
    depends_on:
      - db
    user: "1000:1000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: "30s"
      timeout: "10s"
      retries: 3
      start_period: "15s"
    shm_size: "256m"
    ulimits:
      nofile:
        soft: 65536
        hard: 65536

  db:
    image: postgres:16-alpine
    container_name: my-db
    environment:
      POSTGRES_DB: app
      POSTGRES_USER: app
      POSTGRES_PASSWORD: changeme
    volumes:
      - db-data:/var/lib/postgresql/data
    restart: always
    expose:
      - "5432"
    stop_grace_period: "30s"

volumes:
  web-data: {}
  db-data: {}

networks:
  app-net:
    name: my-network
    external: true

configs:
  nginx-conf:
    content: |
      worker_processes 1;
      events { worker_connections 1024; }
      http {
        server {
          listen 80;
          server_name [accessIP];
          location / {
            proxy_pass http://[containerIP]:3000;
          }
        }
      }
```

## Store File (app-store-urls)

```yaml
# my-store.tikappstore.yaml
- name: app-one
  descr: First app in the store
  category: networking
  services:
    main:
      image: nginx:alpine
      ports:
        - "8080:80/tcp"

- name: app-two
  descr: Second app in the store
  category: monitoring
  services:
    grafana:
      image: grafana/grafana:latest
      ports:
        - "3000:3000/tcp:web"
      environment:
        GF_SECURITY_ADMIN_PASSWORD: admin
      volumes:
        - grafana-data:/var/lib/grafana
  volumes:
    grafana-data: {}
```

## Port Format Examples

```yaml
# === Old OCI-style (all RouterOS versions) ===
ports:
  - "8080:80"                          # No protocol (defaults to tcp)
  - "8080:80/tcp"                      # Explicit tcp
  - "53:53/udp"                        # UDP
  - "8080:80/tcp:web"                  # With label
  - "192.168.1.1:8080:80/tcp"         # With bind IP
  - "[accessIP]:[accessPort]:80/tcp"   # With placeholders

# === New RouterOS 7.23+ style ===
ports:
  - "8080:80:web:tcp"                  # Label then protocol
  - "53:53:dns:udp"                    # UDP with label
  - "[accessIP]:[accessPort]:80:web:tcp"  # With placeholders

# === Long-form object syntax ===
ports:
  - target: 80
    published: 8080
    protocol: tcp
    name: web
    app_protocol: http
```

## Placeholder Usage

```yaml
services:
  web:
    image: nginx:alpine
    ports:
      - "[accessIP]:[accessPort]:80/tcp:web"
    environment:
      # These expand to actual IPs/ports at deploy time
      PUBLIC_URL: "http://[accessIP]:[accessPort]"
      INTERNAL_IP: "[containerIP]"
      ROUTER: "[routerIP]"
```
