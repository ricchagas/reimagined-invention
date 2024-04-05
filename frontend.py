from logging import getLogger
from fastapi.routing import APIRouter
from api_base import create_default_payload
from fastapi.responses import HTMLResponse

router = APIRouter()
logger = getLogger(__name__)

@router.get("/", response_class=HTMLResponse)
async def read_html():

    """Retorna o conteúdo do arquivo index.html. 
       para nao complicar, vamos carregar o arquivo html e retornar o conteudo dele."""
    with open("index.html", "r") as html_file:
        return HTMLResponse(content=html_file.read())
