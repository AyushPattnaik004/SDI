sudo lsof -ti:11116 | xargs sudo kill -9

cd /

cd home/azureuser/BLS

uvicorn apiserver_main:app --host 0.0.0.0 --port 11116 --ssl-keyfile citylytics.key --ssl-certfile ca-bundle.crt &