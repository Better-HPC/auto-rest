# Running in Production

When running Auto-REST in production, it is strongly recommended to deploy the generated server behind a reverse proxy.
In additional to their many implicit benefits, modern proxies offer advanced configuration options that Auto-REST alone
does not.

The following documentation highlights common proxy features for consideration by administrators.
The Nginx proxy is used in examples for demonstrative purposes.
Examples are provided for clarification and as a starting point for administrators.
They are not intended for use as-is.

## Enforcing TLS

It is generally considered good practice to prevented unencrypted connections from accessing APIs.
Administrators may choose to block these connections outright, or redirect them to a port requiring encryption.

!!! example "Example: Redirecting to TLS"

    The following example redirects unencrypted requests to a port requiring TLS.
    It is assumed the API server is running on `http://localhost:8081` and SSL certificates are available under `/etc/ssl`.

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

## User Authentication

Authentication can be enforced at the proxy level, ensuring that only verified users can access the API.
This can be used to protect private APIs or enforce login requirements before requests reach the backend server.

!!! example "Example: Nginx Basic Authentication"

    The configuration below uses an _HTTP Basic Authentication_ scheme which requires users to authenticate with a
    username and password. User credentials are managed using the `htpasswd` utility, which stores hashed user credentials
    in a `/etc/nginx/.htpasswd` file.
    
    ```nginx
    server {
        listen 443 ssl;
        server_name api.example.com;
    
        # SSL configuration
        ssl_certificate /etc/ssl/certs/fullchain.pem;
        ssl_certificate_key /etc/ssl/private/privkey.pem;
    
        # Enable Basic Authentication
        auth_basic           "Restricted API";
        auth_basic_user_file /etc/nginx/.htpasswd;
    
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

Rate-limiting provides a safeguard from malicious clients seeking to overwhelm a server with excessive requests.
These limits may be applied globally, or on a per-client basis for more refined control.

!!! example "Example: Nginx Rate Limiting"

    The following configuration demonstrates rate limiting using the `limit_req_zone` directive.
    The `api_limit` policy enforces a limit of 10 requests per second (`10r/s`) per user (`$binary_remote_addr`).
    The burst parameter allows a temporary burst of up to 20 requests, allowing momentary surges before applying the policy.

    ```nginx
    server {
        limit_req_zone $binary_remote_addr zone=api_limit rate=10r/s;
        location / {
            limit_req zone=api_limit burst=20;
        }
    }
    ```

## Enforcing CORS Policies

Cross-Origin Resource Sharing (CORS) prevents requests from unauthorized sources against the server.
It restricts clients from submitting requests from unrecognized origins, unless explicitly allowed by the target server.
This mechanism helps mitigate unauthorized data access from malicious third-party websites.

!!! example "Example: Nginx CORS Configuration"

    The configuration below demonstrates a basic CORS policy using the `add_header` directive.
    This setup allows requests from any origin (`Access-Control-Allow-Origin: '*'`) and limits the supported
    HTTP methods to those explicitly listed.

    ```nginx
    server {
        location / {
            add_header 'Access-Control-Allow-Origin' '*';
            add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS, HEAD';
            add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type';
        }
    }
    ```