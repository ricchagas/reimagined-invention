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
            logger.info(f"Chamando a api {server}{url}")
            resposta_externa = await client.get(f"http://{server}{url}", params=kwargs)
            return resposta_externa.json(), resposta_externa.status_code
        except Exception as e:
            logger.error(f"Erro ao chamar a api {server}{url}", exc_info=True, extra={"error": str(e)})
            raise HTTPException(status_code=500, detail={"error": str(e)})
        
def extract_metadata (raw_data, status_code = 200):
    try:
        container = raw_data.get("metadata")

        if not container:
            container = raw_data.get("detail")['metadata']

        ip_servidor = [x for x in container.get("ip_do_servidor") if x != "127.0.0.1"]
        nome_do_servidor = container.get("nome_do_servidor")
        versao = container.get("env")["VERSION"]

        return {"ip_servidor": ip_servidor, "nome_do_servidor": nome_do_servidor, "versao": versao, "status_code": status_code}
    except Exception as e:
        return None
    


@router.get("/info")
async def get_info(estado: str, cidade: str):
    """Retorna informações sobre a cidade e estado informados.
    primeiro faz a busca da informacao a partir da api de populacao, depois da api de latitude e por fim da api de clima.
    """

    status_waether, status_populacao, status_latitude = 0, 0, 0
    resposta = {}
    resposta["cidade"] = cidade
    resposta["estado"] = estado
    
    ## chamando as apis
    resposta_populacao, status_populacao =  await call_apl(env.ENDPOINT_SERVIDOR_POPULACAO, f"/populacao", cidade = cidade, estado = estado)
    resposta_latitude, status_latitude = await call_apl(env.ENDPOINT_SERVIDOR_LATITUDE, f"/latitude", cidade = cidade, estado = estado)

    ## faz a chamada da api de clima
    try:
        latitude = resposta_latitude["data"]["latitude"]
        longitude = resposta_latitude["data"]["longitude"]
        waether, status_waether = await call_apl(env.ENDPOINT_SERVIDOR_PREVISAO_TEMPO, f"/clima", latitude = latitude, longitude = longitude)
        
    except Exception as e:
        waether = {"error": str(e)}

    resposta["clima"] = waether

    try:
        resposta["populacao"] = resposta_populacao["data"]["populacao"]
    except Exception as e:
        resposta["populacao"] = resposta_populacao["detail"]["data"]["error"]


    metada = {}
    metada["populacao"] = extract_metadata(resposta_populacao, status_populacao)
    metada["latitude"] = extract_metadata(resposta_latitude, status_latitude)
    metada["clima"] = extract_metadata(waether,status_waether)


    resposta["metadata"] = metada
    

    return resposta
    
    

    