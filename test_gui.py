import gradio as gr
def test():
    updates = [gr.update() for _ in range(50)]
    yield tuple(["msg", "logs"] + updates)

with gr.Blocks() as demo:
    t = gr.Textbox()
    t2 = gr.Textbox()
    a = [gr.Audio() for _ in range(50)]
    b = gr.Button()
    b.click(test, outputs=[t, t2] + a)

if __name__ == "__main__":
    demo.launch(server_port=7866)
