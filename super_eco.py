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
from logging import getLogger
import httpx

from enviroment import env
import api_populacao
import api_waether
import api_latitude
import frontend
import bff


logger = getLogger(__name__)


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
    uvicorn.run("super_eco:app", host="0.0.0.0", port=env.SERVER_PORT, reload=True)
