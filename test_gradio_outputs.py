import gradio as gr
def test_fn():
    yield tuple(["First output", "Second output"] + [{"__type__": "update", "visible": True} for _ in range(2)])

with gr.Blocks() as demo:
    t1 = gr.Textbox()
    t2 = gr.Textbox()
    a1 = gr.Audio()
    a2 = gr.Audio()
    btn = gr.Button("test")
    btn.click(test_fn, outputs=[t1, t2, a1, a2])

demo.launch(server_port=7861, prevent_thread_lock=True)
