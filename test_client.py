from gradio_client import Client
client = Client("http://127.0.0.1:7862")
result = client.predict(api_name="/predict")
print(result)
