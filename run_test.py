from gradio_client import Client
c = Client("http://127.0.0.1:7864")
res = c.predict(api_name="/test")
print("LEN:", len(res))
