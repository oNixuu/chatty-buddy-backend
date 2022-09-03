#pakiety: pymongo, python-socketio, uvicorn, websockets, aiohttp
import sys
import subprocess
from data import deploy_db

#System req
pakiety = ['pymongo', 'python-socketio', 'uvicorn', 'websockets', 'aiohttp']

def install(packages):
    for n in packages:
        subprocess.check_call([sys.executable, "-m", "pip", "install", n])

if __name__=='__server_setup__':
    install(pakiety)
    deploy_db()