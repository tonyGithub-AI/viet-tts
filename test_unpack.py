import gradio as gr

def generate():
    yield tuple(["message 1", "message 2"])
    yield tuple(["message 3", "message 4"])

with gr.Blocks() as demo:
    t1 = gr.Textbox(label="1")
    t2 = gr.Textbox(label="2")
    btn = gr.Button("run")
    btn.click(generate, outputs=[t1, t2])

demo.launch(prevent_thread_lock=True, server_port=7862)
