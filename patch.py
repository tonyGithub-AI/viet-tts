import re

with open("tts_web.py", "r") as f:
    content = f.read()

# 1. Update read_aloud function
read_aloud_old = """def read_aloud(text, speed, progress=gr.Progress(track_tqdm=True)):
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

    audio_paths = [None] * n_chunks"""

read_aloud_new = """MAX_CHUNKS = 50

def read_aloud(text, speed, progress=gr.Progress(track_tqdm=True)):
    global tmp_files

    audio_updates = [gr.update(visible=False, value=None)] * MAX_CHUNKS

    if not text or not text.strip():
        yield ["Enter text first!", ""] + audio_updates
        return

    # Pre-check server
    if not is_server_ready():
        yield ["❌ Connection Error: Backend server is offline.", "Server unreachable at " + VIET_TTS_URL] + audio_updates
        return

    text = text.strip()
    progress(0, desc="Smart-splitting...")
    chunks = smart_split(text)
    n_chunks = len(chunks)
    if n_chunks > MAX_CHUNKS:
        n_chunks = MAX_CHUNKS
        chunks = chunks[:MAX_CHUNKS]"""

content = content.replace(read_aloud_old, read_aloud_new)

# 2. Update yield statements
content = content.replace(
    'yield [p for p in audio_paths if p], f"⏳ Synthesizing Chunk 1/{n_chunks}... ({seconds_waited:.1f}s)", ""',
    'yield [f"⏳ Synthesizing Chunk 1/{n_chunks}... ({seconds_waited:.1f}s)", ""] + audio_updates'
)
content = content.replace(
    'audio_paths[0] = first_wav',
    'audio_updates[0] = gr.update(visible=True, value=first_wav, autoplay=True)'
)
content = content.replace(
    'yield [p for p in audio_paths if p], f"⚡ Chunk 1 ready! Starting playback while processing others...", ""',
    'yield [f"⚡ Chunk 1 ready! Starting playback while processing others...", ""] + audio_updates'
)
content = content.replace(
    'yield [p for p in audio_paths if p], "✅ Complete: 1 chunk synthesized.", "Success"',
    'yield ["✅ Complete: 1 chunk synthesized.", "Success"] + audio_updates'
)
content = content.replace(
    'audio_paths[idx] = wav',
    'audio_updates[idx] = gr.update(visible=True, value=wav, autoplay=False)'
)
content = content.replace(
    'yield [p for p in audio_paths if p], f"🔄 Synthesized {completed}/{n_chunks} chunks...", ""',
    'yield [f"🔄 Synthesized {completed}/{n_chunks} chunks...", ""] + audio_updates'
)
content = content.replace(
    'yield [p for p in audio_paths if p], f"✅ COMPLETE: {n_chunks} chunks ready sequentially.", "Success"',
    'yield [f"✅ COMPLETE: {n_chunks} chunks ready sequentially.", "Success"] + audio_updates'
)

# 3. Update UI Layout
layout_old = """            audio_state = gr.State([])
            @gr.render(inputs=audio_state)
            def render_audio(paths):
                if not paths:
                    gr.Markdown("*Audio will appear here chunk-by-chunk...*")
                for i, p in enumerate(paths):
                    gr.Audio(value=p, label=f"▶️ Part {i+1}", interactive=False, autoplay=(i == 0))
            
            status = gr.Textbox(label="📊 Progress Info", interactive=False)"""

layout_new = """            status = gr.Textbox(label="�� Progress Info", interactive=False)
            gr.Markdown("*Audio will appear here chunk-by-chunk...*")
            audio_players = []
            for i in range(MAX_CHUNKS):
                audio_players.append(gr.Audio(label=f"▶️ Part {i+1}", interactive=False, visible=False))

            gr.HTML(\"\"\"
            <script>
            setInterval(function() {
                var audios = document.querySelectorAll('audio');
                for(var i=0; i<audios.length; i++) {
                    if(!audios[i].hasAttribute('chained')) {
                        audios[i].setAttribute('chained', 'true');
                        audios[i].addEventListener('ended', function(e) {
                            var allAudios = Array.from(document.querySelectorAll('audio'));
                            var idx = allAudios.indexOf(e.target);
                            if(idx >= 0 && idx < allAudios.length - 1) {
                                var nextAudio = allAudios[idx + 1];
                                if (nextAudio && nextAudio.src && nextAudio.src.indexOf('blob:') !== -1 || nextAudio.src.indexOf('file=') !== -1 || nextAudio.src !== "") {
                                    // A small delay to ensure UI updates are complete
                                    setTimeout(() => { nextAudio.play(); }, 500);
                                }
                            }
                        });
                    }
                }
            }, 1000);
            </script>
            \"\"\")"""

content = content.replace(layout_old, layout_new)

# 4. Update the Button click event
btn_old = "btn.click(read_aloud, inputs=[textbox, speed_slider], outputs=[audio_state, status, technical_log])"
btn_new = "btn.click(read_aloud, inputs=[textbox, speed_slider], outputs=[status, technical_log] + audio_players)"
content = content.replace(btn_old, btn_new)

with open("tts_web.py", "w") as f:
    f.write(content)
print("done")
