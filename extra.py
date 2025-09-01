
import socket, os, sys
host = os.getenv("API_BASE","http://api:8000").split("://",1)[-1].split("/",1)[0].split(":")[0]
try:
    ip = socket.gethostbyname(host)
    print("RESOLVED:", host, "->", ip)
except Exception as e:
    print("RESOLVE-ERROR:", host, e)
