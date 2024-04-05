"""
    Arquivo de configuração do projeto
    - Carrega as configurações a partir de arquivos excel
"""
import os
import sys
sys.path.insert(1, os.getcwd())
import logging
logger = logging.getLogger(__name__)

class Environment:
    """ Class with the environment variables
    """
    pass

env = Environment()

logger.info("loading enviroment from files ")


setattr(env, 'VERSION', int(os.environ.get("VERSION", '3')))
setattr(env, 'ENDPOINT_SERVIDOR_POPULACAO', os.environ.get("ENDPOINT_SERVIDOR_POPULACAO", '127.0.0.1'))
setattr(env, 'ENDPOINT_SERVIDOR_LATITUDE', os.environ.get("ENDPOINT_SERVIDOR_LATITUDE", '127.0.0.1'))
setattr(env, 'ENDPOINT_SERVIDOR_PREVISAO_TEMPO', os.environ.get("ENDPOINT_SERVIDOR_PREVISAO_TEMPO", '127.0.0.1'))
# setattr(env, 'ENDPOINT_SERVIDOR_POPULACAO', os.environ.get("ENDPOINT_SERVIDOR_POPULACAO", ''))
setattr(env, 'SERVER_PORT', int(os.environ.get("SERVER_PORT", '8000')))
setattr(env, 'APPLICATION_FIXED', int(os.environ.get("APPLICATION_FIXED", '1')))
setattr(env, 'MENSAGEM_ECO', os.environ.get("MENSAGEM_ECO", 'Mensagem Padrao'))

logger.info("enviroment loaded")