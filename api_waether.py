from fastapi import HTTPException
from fastapi.routing import APIRouter
import json
import random 
from enviroment import env
from logging import getLogger
import httpx
from api_base import create_default_payload

router = APIRouter()
logger = getLogger(__name__)


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


def generate_response (raw_data):
    response = {}
    response["waether"] = {}
    response["waether"]["temperature_2m"] = f'{raw_data["current"]["temperature_2m"]} : {raw_data["current_units"]["temperature_2m"]}'
    response["waether"]["wind_speed_10m"] = f'{raw_data["current"]["wind_speed_10m"]} : {raw_data["current_units"]["wind_speed_10m"]}'

    if env.VERSION > 2:
        max_response = 48

        response["waether"]["hourly"] = []
        ct  = 0
        for i, item in enumerate(raw_data["hourly"]["time"]):
            response["waether"]["hourly"].append( {"hour": item,  
                                                   "temperature_2m": f'{raw_data["hourly"]["temperature_2m"][i]}'
                                                    })
            ct += 1
            if ct > max_response:
                break

    return response

@router.get("/clima")
async def get_populacao(latitude: float, longitude: float):

    await sucess_or_fail()

    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m&hourly=temperature_2m"

    async with httpx.AsyncClient(verify=False) as client:
        try:
            resposta_externa = await client.get(url)
            if resposta_externa.status_code == 200:
                # Adiciona a resposta externa ao array de respostas
                to_return = resposta_externa.json()
                return await create_default_payload(generate_response(to_return))
            else:
                raise HTTPException(status_code=500, detail=await create_default_payload({"error": "Falha ao chamar servidor externo."}))
        except Exception as e:
            raise HTTPException(status_code=500, detail=await create_default_payload({"error": str(e)}))

