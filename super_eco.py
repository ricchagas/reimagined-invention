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
import uvicorn
import logging 
import httpx

from enviroment import env
import api_populacao
import api_waether
import api_latitude
import frontend
import bff


logging.basicConfig(level=logging.INFO)



logger = logging.getLogger(__name__)


# if ENDPOINT_SERVIDOR:
#     logger.info(f"Endpoint do servidor: {ENDPOINT_SERVIDOR}")
# else:   
#     logger.info("Endpoint do servidor não foi definido, assumindo valor padrão.")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas as origens
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos
    allow_headers=["*"],  # Permite todos os cabeçalhos
)
             
app.include_router(api_populacao.router)
app.include_router(api_waether.router)
app.include_router(api_latitude.router)
app.include_router(frontend.router)
app.include_router(bff.router)

if __name__ == "__main__":
    logger.info("Iniciando a aplicacao")
    uvicorn.run("super_eco:app", host="0.0.0.0", port=env.SERVER_PORT, reload=True)
