### Start the app in dev mode

```
python market_data_server.py
```

### Start the app with WSGI

Without SSL:

```
gunicorn -b 0.0.0.0:12342 wsgi:app
```

With SSL:

```
gunicorn --certfile certs/cert.pem --keyfile certs/privkey.pem --bind 0.0.0.0:12342 wsgi:app
```
