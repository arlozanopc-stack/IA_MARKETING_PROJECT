import os
from dotenv import load_dotenv

# Carga las variables del archivo .env
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")