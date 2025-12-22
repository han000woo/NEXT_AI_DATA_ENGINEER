import time

def stream_data(response):
    for word in response.split(" "):
        yield word + " "
        time.sleep(0.1)