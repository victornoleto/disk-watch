# Install

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

# Configure webserver

## Supervisor

`sudo nano /etc/supervisor/conf.d/disk-watch.conf`

```
[program:disk-watch]
directory=/var/www/disk-watch
command=/var/www/disk-watch/venv/bin/gunicorn app:app -b localhost:4040
autostart=true
autorestart=true
stderr_logfile=/var/www/disk-watch/log/err.log
stdout_logfile=/var/www/disk-watch/log/out.log
```

`sudo supervisorctl reread && sudo supervisorctl update`

Check if is running: `sudo supervisorctl status`

## Nginx

`sudo nano /etc/nginx/sites-enabled/disk-watch`

```
server {
    listen 81;
    server_name disk-watch.local;

    location / {
        proxy_pass http://127.0.0.1:4040;
    }
}
```

```
sudo nginx -t
sudo service nginx restart
```

# Configure schedule

`crontab -e`

```
*/10 * * * * cd /var/www/disk-watch && /venv/bin/python3 watch.py
```