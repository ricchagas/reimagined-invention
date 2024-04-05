from fastapi import HTTPException
from fastapi.routing import APIRouter
import json
import random 
from enviroment import env
from logging import getLogger

router = APIRouter()
logger = getLogger(__name__)

with open("data/municipio_latitude_all.json") as f:
    populacao_data = json.load(f)

from api_base import create_default_payload

if env.VERSION == 1:
    """Caso seja a versão 1, deixa somente 10 cidades por estado"""
    populacao_data = [item for item in populacao_data if item["municipio"] in ["São Paulo", "Rio de Janeiro", "Belo Horizonte", "Curitiba", "Porto Alegre", "Florianópolis", "Brasília", "Salvador", "Recife", "Fortaleza"]]

success_rate = 0.5  
if env.VERSION == 2:
    success_rate = 0.7
elif env.VERSION == 3:
    success_rate = 1

async def sucess_or_fail():
    luck_number = random.random()
    logger.info(f"luck_number: {luck_number}")

    if luck_number > success_rate:
        raise HTTPException(status_code=500, detail=await create_default_payload({"error": f"Internal Server Error: bad luck number, sucess rate is {success_rate:.2f} and you got {luck_number}"}))


@router.get("/latitude")
async def get_populacao(cidade: str, estado: str):

    await sucess_or_fail()

    for item in populacao_data:
        if item["municipio"].lower() == cidade.lower() and item["uf"].lower() == estado.lower():
            return await create_default_payload(item)
    raise HTTPException(status_code=404, detail=await create_default_payload({"error": "Not Found"}))
