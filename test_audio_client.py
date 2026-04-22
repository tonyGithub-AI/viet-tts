from gradio_client import Client
c = Client("http://127.0.0.1:7865")
print(c.predict(api_name="/test"))
