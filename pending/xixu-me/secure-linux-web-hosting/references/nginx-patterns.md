# Nginx Patterns

This reference keeps the two hosting outcomes separate on purpose:

- static-site hosting
- reverse-proxy hosting

Choose the branch that matches the user's goal. Do not merge both into one
default answer unless the user clearly needs a hybrid setup.

## Shared Preconditions

Before either branch:

- verify the distro-specific Nginx package and config layout from official docs
- install and start Nginx
- validate the config with `nginx -t`
- confirm the service is healthy
- intentionally open ports `80` and `443` only when the web path is ready

## Static-Site Pattern

Use this branch when the user wants Nginx to serve files directly.

Typical ingredients:

- a chosen document root
- an `index.html` or equivalent entry file
- readable file permissions for the Nginx worker account or policy
- a simple `server` block with `root` and `index`

Minimal shape:

```nginx
server {
    listen 80;
    server_name example.com www.example.com;

    root /srv/www/example;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }
}
```

Verify in this order:

1. `nginx -t`
2. reload Nginx
3. `curl -I http://example.com`
4. open the site in a browser

Common failure branch:

- if the server block looks right but the site fails, check the `root` path,
  file permissions, and any SELinux/AppArmor policy before assuming DNS is the
  problem

## Reverse-Proxy Pattern

Use this branch when the actual app should stay bound to loopback and Nginx
fronts it.

Safe default:

- the app listens on `127.0.0.1:<port>`
- Nginx is the only public-facing process

Minimal shape:

```nginx
server {
    listen 80;
    server_name example.com www.example.com;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Verify in this order:

1. confirm the app responds locally on the server first
2. `nginx -t`
3. reload Nginx
4. `curl -I http://example.com`

Common failure branch:

- if Nginx is healthy but the site is down, check whether the app is listening
  on the expected loopback port, whether the service is running, and whether
  policy controls such as SELinux are blocking the proxy connection

## Branch Boundary Rules

- For a static site, do not invent an upstream app port.
- For a reverse proxy, do not tell the user to expose the app port publicly.
- If the app needs websockets, streaming, or long-lived connections, verify the
  extra Nginx directives from current official docs instead of assuming the
  minimal proxy block is sufficient.
