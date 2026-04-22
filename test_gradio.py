import gradio as gr

def test():
    updates = [gr.update(visible=True) for _ in range(3)]
    # yield as tuple
    yield tuple(["status", "logs"] + updates)

with gr.Blocks() as demo:
    t1 = gr.Textbox(label="Status")
    t2 = gr.Textbox(label="Logs")
    audios = [gr.Audio(label=f"A{i}") for i in range(3)]
    b = gr.Button()
    b.click(test, outputs=[t1, t2] + audios)

demo.launch(server_port=7864)
