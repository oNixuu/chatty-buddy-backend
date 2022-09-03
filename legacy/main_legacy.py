import socketio
from util import get_ip
from aiohttp import web
from kolory import bcolors
from db import user_log_in
import asyncio
import uvicorn as uv

#TODO handle_request do requestów HTTP
ip = get_ip()
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*') # utworzenie serwera Socket.IO
sio.always_connect = False

app = socketio.ASGIApp(sio)
user_sid= {}

@sio.event
async def connect(sid, environ, auth): #Environ is all client data, auth is authorization data passed by client


    print(f'{bcolors.OKGREEN}[+] {bcolors.OKBLUE}Nowy klient połączony: {bcolors.OKGREEN}{sid}{bcolors.ENDC}')
    

    if user_log_in(auth['login'], auth['password']):
        print(f'{bcolors.OKGREEN}Użytkownik {bcolors.OKCYAN}{auth["login"]}{bcolors.OKGREEN} zalogowany{bcolors.ENDC}')
        user_sid[sid] = auth['login'] # Add user to sid list, to identify later requests
        return True # Succeful login attempt
    else:
        print(f'{bcolors.WARNING}Podano złe hasło/login{bcolors.ENDC}')
        sio.disconnect(sid=sid)
        return False # Not succesful login attempt
    


@sio.event
async def disconnect(sid):
    print(f'{bcolors.WARNING}[-] {bcolors.OKBLUE}Klient rozłączony: {bcolors.OKGREEN}{sid}{bcolors.ENDC}')
    #TODO Dodać zmianę statusu aktywności



@sio.event
async def msg(sid, data): #(message, to)
        
    await sio.emit('nmsg', {'login': data['login'], 'message':data['message']})

if __name__ == '__main__':
    uv.run(app, host='25.74.206.90', forwarded_allow_ips=['*'], server_header=False, port=8080)

#uvicorn --reload --host 192.168.224.193 main:app
#25.74.206.90
#uvicorn --reload --forwarded-allow-ips '*' --host 25.74.206.90 main:app