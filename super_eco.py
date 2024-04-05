"""
    Criar o servidor
    SERVER_PORT=8082 python super_eco.py

    Criar o servidor com endpoint do servidor
    SERVER_PORT=8081 ENDPOINT_SERVIDOR=127.0.0.1:8082  python super_eco.py

    Criar o cliente
    ENDPOINT_SERVIDOR=127.0.0.1:8081 python super_eco.py
"""

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, Header,Request
import os
import random
import socket
# from dotenv import load_dotenv
import uvicorn
from netifaces import interfaces, ifaddresses, AF_INET
from logging import getLogger
# import requests
import httpx
from typing import Optional
from fastapi.responses import HTMLResponse



populacao_raw = """
São Paulo - 11451245
Guarulhos - 1291784
Campinas - 1138309
São Bernardo do Campo - 810729
Santo André - 748919
Osasco - 743432
Sorocaba - 723574
Ribeirão Preto - 698259
São José dos Campos - 697428
São José do Rio Preto - 480439
"""

populacao = {}

for linha in populacao_raw.strip().split("\n"):
    cidade, pop = linha.split(" - ")
    populacao[cidade] = int(pop)

logger = getLogger(__name__)

# load_dotenv()  # Take environment variables from .env file
ENDPOINT_SERVIDOR = os.getenv("ENDPOINT_SERVIDOR")
SERVER_PORT = int(os.getenv("SERVER_PORT", 8000))
APPLICATION_FIXED = int(os.getenv("APPLICATION_FIXED", "1"))

if ENDPOINT_SERVIDOR:
    logger.info(f"Endpoint do servidor: {ENDPOINT_SERVIDOR}")
else:   
    logger.info("Endpoint do servidor não foi definido, assumindo valor padrão.")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas as origens
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos
    allow_headers=["*"],  # Permite todos os cabeçalhos
)

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
    mensagem = os.getenv("MENSAGEM_ECO", "Mensagem padrão se variável de ambiente não estiver definida.")

    return {
        "nome_do_servidor": nome_do_servidor,
        "ip_do_servidor": ip_do_servidor,
        "tempo_de_latencia": tempo_de_latencia,
        "mensagem": mensagem,
        "porta": SERVER_PORT,
    }

async def get_populacao(cidade):
    """Isso é pra simular uma chamada a um banco de dados ou algo do tipo.
    Aqui a gente só retorna um valor fixo, mas poderia ser qualquer coisa.
    Também possibilita ter um comportamento diferente se a variável de ambiente permitindo criarmos 2 imagens distintas com o mesmo código fonte.    
    """

    if APPLICATION_FIXED:
        return populacao.get(cidade, "-2")
    else:
        return -1
    
@app.get("/", response_class=HTMLResponse)
async def read_html():

    """Retorna o conteúdo do arquivo index.html. 
       para nao complicar, vamos carregar o arquivo html e retornar o conteudo dele."""
    with open("index.html", "r") as html_file:
        return HTMLResponse(content=html_file.read())


@app.get("/eco")
async def eco(request: Request, cidade: str):
    # Tentativa de obter o cabeçalho x_hop diretamente do objeto Request
    x_hop = request.headers.get('x-hop')  # Use hífen ao invés de underline
    hop_value = 1 if x_hop is None else int(x_hop) + 1
    
    if cidade:
        to_response = {}
        to_response["cidade"] = cidade
        resposta = await get_server_details()
        resposta["populacao"] = await get_populacao(cidade)
        resposta["hop"] = hop_value
        to_response['respostas'] = [resposta]

        if ENDPOINT_SERVIDOR:
            async with httpx.AsyncClient() as client:
                try:
                    resposta_externa = await client.get(f"http://{ENDPOINT_SERVIDOR}/eco?cidade={cidade}", headers={"x-hop": str(hop_value)})
                    if resposta_externa.status_code == 200:
                        # Adiciona a resposta externa ao array de respostas
                        to_response['respostas'].extend(resposta_externa.json()['respostas'])
                    else:
                        to_response['respostas'].append({"erro": "Falha ao chamar servidor externo."})
                except Exception as e:
                    to_response['respostas'].append({"erro": str(e)})
        return to_response
    else:
        raise HTTPException(status_code=400, detail="Cidade é um parâmetro obrigatório.")

if __name__ == "__main__":
    uvicorn.run("super_eco:app", host="0.0.0.0", port=SERVER_PORT, log_level="debug", reload=True)
