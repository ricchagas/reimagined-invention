from netifaces import interfaces, ifaddresses, AF_INET
from enviroment import env
import socket
import os
import random

async def ip4_addresses():
    ip_list = []
    for interface in interfaces():
        try:
            for link in ifaddresses(interface)[AF_INET]:
                ip_list.append(link['addr'])
        except KeyError:
            pass
    return ip_list


async def get_server_details():   
    nome_do_servidor = socket.gethostname()
    ip_do_servidor =  await ip4_addresses()
    tempo_de_latencia = f"{random.randint(1, 100)}ms"
  
    return {
        "nome_do_servidor": nome_do_servidor,
        "ip_do_servidor": ip_do_servidor,
        "tempo_de_latencia": tempo_de_latencia,
        "env": env.__dict__
    }

async def create_default_payload(data):
    return {
        "data": data,
        "metadata": await get_server_details()
    }

    