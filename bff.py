from fastapi import HTTPException
from fastapi.routing import APIRouter
import json
import random 
from enviroment import env
from logging import getLogger
import httpx

router = APIRouter()
logger = getLogger(__name__)

async def call_apl (server, url, **kwargs):
    async with httpx.AsyncClient() as client:
        try:
            resposta_externa = await client.get(f"http://{server}:{env.SERVER_PORT}{url}", params=kwargs)
            return resposta_externa.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail={"error": str(e)})
        
def extract_metadata (raw_data):
    try:
        container = raw_data.get("metadata")

        if not container:
            container = raw_data.get("detail")['metadata']

        ip_servidor = [x for x in container.get("ip_do_servidor") if x != "127.0.0.1"]
        nome_do_servidor = container.get("nome_do_servidor")
        versao = container.get("env")["VERSION"]

        return {"ip_servidor": ip_servidor, "nome_do_servidor": nome_do_servidor, "versao": versao}
    except Exception as e:
        return None
    


@router.get("/info")
async def get_info(estado: str, cidade: str):
    """Retorna informações sobre a cidade e estado informados.
    primeiro faz a busca da informacao a partir da api de populacao, depois da api de latitude e por fim da api de clima.
    """
    resposta = {}
    resposta["cidade"] = cidade
    resposta["estado"] = estado
    
    ## chamando as apis
    resposta_populacao =  call_apl(env.ENDPOINT_SERVIDOR_POPULACAO, f"/populacao", cidade = cidade, estado = estado)
    resposta_latitude = call_apl(env.ENDPOINT_SERVIDOR_LATITUDE, f"/latitude", cidade = cidade, estado = estado)

    resposta_populacao = await resposta_populacao
    resposta_latitude = await resposta_latitude

    ## faz a chamada da api de clima
    try:
        latitude = resposta_latitude["data"]["latitude"]
        longitude = resposta_latitude["data"]["longitude"]
        waether = await call_apl(env.ENDPOINT_SERVIDOR_PREVISAO_TEMPO, f"/clima", latitude = latitude, longitude = longitude)
        
    except Exception as e:
        waether = {"error": str(e)}

    resposta["clima"] = waether

    try:
        resposta["populacao"] = resposta_populacao["data"]["populacao"]
    except Exception as e:
        resposta["populacao"] = resposta_populacao["detail"]["data"]["error"]


    metada = {}
    metada["populacao"] = extract_metadata(resposta_populacao)
    metada["latitude"] = extract_metadata(resposta_latitude)
    metada["clima"] = extract_metadata(waether)


    resposta["metadata"] = metada
    

    return resposta
    
    

    