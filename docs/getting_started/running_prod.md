# Running in Production

Auto-REST supports limited configuration of the deployed server.
Administrators looking for advanced configuration options are encouraged to impliment them via a Reverse proxy.

The example below provides a starting point configuration for an Nginx proxy.
It is assumed the API server is running on `http://localhost:8081` and SSL certificates are available under `/etc/ssl`.

```
server {
    listen 80;
    server_name api.example.com;

    # Redirect HTTP to HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name api.example.com;

    # SSL configuration
    ssl_certificate /etc/ssl/certs/fullchain.pem;
    ssl_certificate_key /etc/ssl/private/privkey.pem;

    # Proxy configuration
    location / {
        proxy_pass http://localhost:8081;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Enforcing Rate Limits

!!! example "Example: Rate Limiting"

    server {

        ... # Base proxy configuration (server name, SSL, etc.)

        # Optional: Rate limiting
        limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
        location / {
            limit_req zone=api_limit burst=20;
        }
    }

## Enforcing CORS Policies

!!! example "Example: CORS Policies"

    server {

        ... # Base proxy configuration (server name, SSL, etc.)
    
        location / {
            add_header 'Access-Control-Allow-Origin' '*';
            add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS, HEAD';
            add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type';
            if ($request_method = 'OPTIONS') {
                return 204;
            }
        }
    }
