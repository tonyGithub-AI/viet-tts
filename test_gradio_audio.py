import gradio as gr
def print_events():
    events = []
    for k, v in gr.Audio.__dict__.items():
        if hasattr(v, '__class__') and v.__class__.__name__ == 'EventListener':
            events.append(k)
    print("gr.Audio events:", events)
print_events()
