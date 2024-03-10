### Start the app in dev mode

```
python market_data_server.py
```

### Start the app with WSGI

Without SSL:

```
gunicorn -b 0.0.0.0:12342 wsgi:app
```
