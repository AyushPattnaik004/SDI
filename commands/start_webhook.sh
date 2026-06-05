sudo lsof -ti:11117 | xargs sudo kill -9

cd /

cd home/azureuser/BLS

uvicorn webhook_main:app --host 0.0.0.0 --port 11117 --ssl-keyfile citylytics.key --ssl-certfile ca-bundle.crt &