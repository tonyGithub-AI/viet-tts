import gradio as gr
import os
import re
import tempfile
import atexit
import subprocess
import time
import traceback
import requests
import concurrent.futures
from openai import OpenAI
from pydub import AudioSegment
from pydub.effects import normalize

# Constants
VIET_TTS_PORT = 8298
VIET_TTS_URL = f"http://localhost:{VIET_TTS_PORT}/v1"

# Cleanup tracker
tmp_files = []

def is_server_ready():
    """Verify if the VietTTS server is responsive."""
    try:
        response = requests.get(f"{VIET_TTS_URL}/voices", timeout=2)
        return response.status_code == 200
    except:
        return False

# Auto-start VietTTS server
def start_viettts():
    if is_server_ready():
        return True, "Server already running."
    
    print(f"Starting VietTTS server on port {VIET_TTS_PORT} with 2 workers...")
    local_bin = os.path.expanduser("~/.local/bin")
    if local_bin not in os.environ["PATH"]:
        os.environ["PATH"] = f"{local_bin}:{os.environ['PATH']}"
    
    # Use 2 workers for parallel synthesis
    subprocess.Popen(["viettts", "server", "--host", "0.0.0.0", "--port", str(VIET_TTS_PORT), "--workers", "2"], 
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=os.environ)
    
    # Poll for readiness
    for i in range(20):
        time.sleep(2)
        if is_server_ready():
            return True, "Server started successfully."
    
    return False, "Server failed to start within 20 seconds. Check logs or manual launch."

def restart_server():
    """Kill any existing viettts process and restart."""
    os.system("pkill -f viettts")
    time.sleep(2)
    return start_viettts()

client = OpenAI(base_url=VIET_TTS_URL, api_key="viet-tts")

def smart_split(text, max_chars=2000):
    """Split into natural sentence chunks (~2K chars for FAST response)."""
    sentences = re.split(r'(?<=[\.!\?])\s+', text)
    chunks, current = [], ""
    for sent in sentences:
        if len(sent) > max_chars:
            if current.strip():
                chunks.append(current.strip())
                current = ""
            words = sent.split()
            temp_chunk = ""
            for word in words:
                if len(word) > max_chars:
                    if temp_chunk.strip():
                        chunks.append(temp_chunk.strip())
                        temp_chunk = ""
                    for i in range(0, len(word), max_chars):
                        chunks.append(word[i:i+max_chars])
                elif len(temp_chunk + word) < max_chars:
                    temp_chunk += word + " "
                else:
                    chunks.append(temp_chunk.strip())
                    temp_chunk = word + " "
            current = temp_chunk
        elif len((current + sent).strip()) < max_chars:
            current += sent + " "
        else:
            chunks.append(current.strip())
            current = sent + " "
    
    if current.strip():
        chunks.append(current.strip())
    return chunks

def synth_chunk(i, chunk, speed):
    """Synthesize a single chunk and return its filepath."""
    try:
        resp = client.audio.speech.create(
            model="tts-1",
            voice="nguyen-ngoc-ngan",
            input=chunk,
            speed=float(speed)
        )
        tmp_chunk = tempfile.NamedTemporaryFile(suffix=f"_chunk{i}.wav", delete=False)
        for bytes_chunk in resp.stream(1 << 20):
            if bytes_chunk:
                tmp_chunk.write(bytes_chunk)
        tmp_chunk.close()
        
        # Audio normalization
        seg = normalize(AudioSegment.from_wav(tmp_chunk.name))
        seg.export(tmp_chunk.name, format="wav")
        return tmp_chunk.name
    except Exception as e:
        print(f"Error in synth_chunk {i}: {e}")
        return None

def read_aloud(text, speed, progress=gr.Progress(track_tqdm=True)):
    global tmp_files

    if not text or not text.strip():
        yield [], "Enter text first!", ""
        return

    # Pre-check server
    if not is_server_ready():
        yield [], "❌ Connection Error: Backend server is offline.", "Server unreachable at " + VIET_TTS_URL
        return

    text = text.strip()
    progress(0, desc="Smart-splitting...")
    chunks = smart_split(text)
    n_chunks = len(chunks)
    
    audio_paths = [None] * n_chunks
    
    # FAST approach: Generate first chunk immediately
    progress(0, desc=f"FAST START: Chunk 1/{n_chunks}")
    first_wav = synth_chunk(0, chunks[0], speed)
    if first_wav:
        audio_paths[0] = first_wav
        tmp_files.append(first_wav)
        yield [p for p in audio_paths if p], f"⚡ Chunk 1 ready! Starting playback while processing others...", ""
    
    if n_chunks == 1:
        yield [p for p in audio_paths if p], "✅ Complete: 1 chunk synthesized.", "Success"
        return

    # Background parallel synthesis for remaining chunks
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        future_to_idx = {executor.submit(synth_chunk, i, chunks[i], speed): i for i in range(1, n_chunks)}
        
        # Results as they finish
        completed = 1
        for future in concurrent.futures.as_completed(future_to_idx):
            idx = future_to_idx[future]
            wav = future.result()
            if wav:
                audio_paths[idx] = wav
                tmp_files.append(wav)
                
                completed += 1
                progress(completed/n_chunks, desc=f"Processed {completed}/{n_chunks} chunks")
                yield [p for p in audio_paths if p], f"🔄 Synthesized {completed}/{n_chunks} chunks...", ""

    yield [p for p in audio_paths if p], f"✅ COMPLETE: {n_chunks} chunks ready sequentially.", "Success"

# Cleanup on exit
def cleanup():
    global tmp_files
    for f in tmp_files:
        if os.path.exists(f):
            try: os.remove(f)
            except: pass
atexit.register(cleanup)

# UI Logic
def ui_restart():
    success, msg = restart_server()
    return f"Status: {msg}"

# UI Layout
with gr.Blocks(title="VietTTS Reader") as demo:
    gr.Markdown("""
    # 🗣️ Vietnamese TTS Book Reader
    **Paste 16-20K chapters** → Auto-chunks → Young female voice (**nguyen-ngoc-ngan**).
    """)

    with gr.Row():
        with gr.Column(scale=3):
            textbox = gr.Textbox(
                lines=25,
                placeholder="Paste your full Vietnamese chapter here...",
                label="📖 Text Canvas",
            )
        
        with gr.Column(scale=1):
            server_status = gr.Markdown("Status: Checking...")
            server_btn = gr.Button("🔄 Restart Backend Server", variant="secondary", size="sm")
            speed_slider = gr.Slider(0.5, 2.0, value=1.0, step=0.1, label="⚡ Speed")
            gr.Markdown("---")
            btn = gr.Button("🎤 Read Aloud (FAST Approach)", variant="primary", size="lg")
            
            audio_state = gr.State([])
            @gr.render(inputs=audio_state)
            def render_audio(paths):
                if not paths:
                    gr.Markdown("*Audio will appear here chunk-by-chunk...*")
                for i, p in enumerate(paths):
                    gr.Audio(value=p, label=f"▶️ Part {i+1}", interactive=False, autoplay=(i == 0))
            
            status = gr.Textbox(label="📊 Status", interactive=False)

    with gr.Accordion("🛠️ Technical Details / Full Error Report", open=False):
        technical_log = gr.Code(label="Traceback Log", language="python", interactive=False)

    gr.Markdown("*Optimal: 0.8-1.2x for audiobooks. ~5-10min synth for 20K chars.*")

    # Bindings
    btn.click(read_aloud, inputs=[textbox, speed_slider], outputs=[audio_state, status, technical_log])
    server_btn.click(ui_restart, outputs=[server_status])
    
    # On Load check
    demo.load(lambda: f"Status: {'🟢 Online' if is_server_ready() else '🔴 Offline'}", outputs=[server_status])

if __name__ == "__main__":
    start_viettts()
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False, inbrowser=False, theme=gr.themes.Soft())
