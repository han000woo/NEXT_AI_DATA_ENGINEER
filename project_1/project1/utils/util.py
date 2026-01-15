import time
import json 

def stream_data(response):
    for word in response.split(" "):
        yield word + " "
        time.sleep(0.1)

def parse_list(text: str) -> list[str]:
    try:
        return json.loads(text)
    except Exception:
        return []