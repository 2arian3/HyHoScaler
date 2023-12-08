import os
from dotenv import load_dotenv


load_dotenv()


PROMETHEUS_URL = f"http://{os.getenv('PROMETHEUS_HOST')}:{os.getenv('PROMETHEUS_PORT')}"