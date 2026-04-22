from gradio_client import Client
client = Client("http://127.0.0.1:7863")
res = client.predict(api_name="/test")
print(len(res))
try:
    print(type(res), type(res[0]), type(res[1]))
except:
    pass
