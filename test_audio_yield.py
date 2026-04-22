import gradio as gr

def test():
    yield tuple(["status", "logs", gr.Audio(visible=True, value="test.wav", autoplay=True)])

with gr.Blocks() as demo:
    t1 = gr.Textbox()
    t2 = gr.Textbox()
    a1 = gr.Audio(visible=False)
    b = gr.Button()
    b.click(test, outputs=[t1, t2, a1])

try:
    demo.launch(server_port=7865)
except Exception as e:
    print(e)
