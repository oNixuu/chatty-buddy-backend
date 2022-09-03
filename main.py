from logging import critical
import socketio
from util import get_ip
from aiohttp import web
from kolory import bcolors
from data import user_log_in, add_message, get_messages, add_user
import asyncio
import uvicorn as uv


ip = get_ip()

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*') # utworzenie serwera Socket.IO
sio.always_connect = False
static_files = {'/':'HTML/site1/'} #API aplikacji



app = socketio.ASGIApp(sio, static_files=static_files)
user_sid= {}
"""
login1 : sid1
sid1 : login1
login2 : sid2
sid2 : login2
"""

@sio.event
async def connect(sid, environ, auth): #Environ is all client data, auth is authorization data passed by client

    print(f'{bcolors.OKGREEN}[+] {bcolors.OKBLUE}Nowy klient połączony: {bcolors.OKGREEN}{sid}{bcolors.ENDC}')
    

    if user_log_in(auth['login'], auth['password']):
        print(f'{bcolors.OKGREEN}Użytkownik {bcolors.OKCYAN}{auth["login"]}{bcolors.OKGREEN} zalogowany{bcolors.ENDC}')
        user_sid[auth['login']] = sid  # Add user to sid list, to identify later requests
        user_sid[sid] = auth['login'] # Add sid to user
        return True # Succeful login attempt
    else:
        print(f'{bcolors.WARNING}Podano złe hasło/login{bcolors.ENDC}')
        await sio.disconnect(sid=sid)
        return False # Not succesful login attempt

@sio.event
async def disconnect(sid):
    print(f'{bcolors.WARNING}[-] {bcolors.OKBLUE}Klient rozłączony: {bcolors.OKGREEN}{sid}{bcolors.ENDC}')
    
    if sid in user_sid:
        del user_sid[user_sid[sid]] # deleting login : sid
        del user_sid[sid] # deleting sid : login

@sio.event
async def msg(sid, data): #(message, to)
    user = user_sid[sid]
    message = data['message']
    reciver = data['to']

    if reciver in user_sid:
        await sio.emit('nmsg', {'sender':user, 'message':message, 'to': reciver}, room=user_sid[reciver])
        await sio.emit('nmsg', {'sender':user, 'message':message, 'to': reciver}, room=sid)
    else:
        await sio.emit('nmsg', {'sender':user, 'message':message, 'to': reciver}, room=sid)
    
    add_message(user, reciver, message)
    
@sio.event
async def g_msg(sid, data):
    user = user_sid[sid]
    message = data['message']
    add_message() #TODO message storing system
    await sio.emit('g_nmsg', {'sender' : user, 'message': message})
    
@sio.event
async def new_user(sid, data):
    return add_user(data['login'], data['password'])

@sio.event
async def fetch(sid, data):
    user = user_sid[sid]
    j_data = get_messages(data['user'], user)
    return j_data

class ChatFetch(socketio.AsyncNamespace):
    def on_connect(self, sid, environ):
        print('FETCH FETCH FETCH FETCH')
        return True
    
    def on_fetch(self, sid, data): #user
        user = user_sid(sid)
        j_data = get_messages(data['user'], user)
        print(j_data)
        sio.send(data=j_data, room=sid)


if __name__ == '__main__':
    uv.run(app, host=ip, forwarded_allow_ips=['*'], server_header=False, port=8080)
    sio.register_namespace(ChatFetch('/chat'))

#uvicorn --reload --host 192.168.224.193 main:app
#25.74.206.90
#uvicorn --reload --forwarded-allow-ips '*' --host 25.74.206.90 main:app