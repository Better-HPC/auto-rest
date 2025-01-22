# Running in Production

When running Auto-REST in production, it is strongly recommended to deploy the generated server behind a reverse proxy.
In additional to their many implicit benefits, modern proxies offer advanced configuration options that Auto-REST alone does not.
This section highlights key features of Nginx that administrators should consider when deploying Auto-REST.
It is not meant to replace the official Nginx documentation but to provide a useful starting point for configuration.

## Enforcing TLS

The following example demonstrates how to configure an Nginx proxy to enforce TLS.
It is assumed the API server is running on `http://localhost:8081` and SSL certificates are available under `/etc/ssl`.

!!! example "Example: Redirecting to TLS"

    ```nginx
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

Nginx provides rate-limiting capabilities to safeguard the server from excessive client requests.
The configuration below demonstrates how to configure rate limiting using the `limit_req_zone` directive.
The `api_limit` policy enforces a limit of 10 requests per second (`10r/s`) per user (`$binary_remote_addr`).
The burst parameter allows a temporary burst of up to 20 requests, enabling brief surges in traffic before throttling
takes effect.

!!! example "Example: Nginx Rate Limiting"

    ```nginx
    server {
        limit_req_zone $binary_remote_addr zone=api_limit rate=10r/s;
        location / {
            limit_req zone=api_limit burst=20;
        }
    }
    ```

## Enforcing CORS Policies

Nginx offers support for enforcing Cross-Origin Resource Sharing (CORS) policies.
The configuration below demonstrates how to implement a basic CORS policy using the `add_header` directive.
This setup allows requests from any origin (`Access-Control-Allow-Origin: '*'`) and limits the supported HTTP methods.

!!! example "Example: Nginx CORS Configuration"

    ```nginx
    server {
        location / {
            add_header 'Access-Control-Allow-Origin' '*';
            add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS, HEAD';
            add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type';
        }
    }
    ```