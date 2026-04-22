import os
import subprocess
import time
import requests
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn
import atexit

VIET_TTS_PORT = 8298
VIET_TTS_URL = f"http://localhost:{VIET_TTS_PORT}/v1"
UI_PORT = 7860

app = FastAPI()
tts_process = None

def is_server_ready():
    try:
        response = requests.get(f"{VIET_TTS_URL}/voices", timeout=2)
        return response.status_code == 200
    except:
        return False

def start_viettts():
    global tts_process
    os.system("pkill -9 -f viettts")
    time.sleep(1)
    
    local_bin = os.path.expanduser("~/.local/bin")
    if local_bin not in os.environ["PATH"]:
        os.environ["PATH"] = f"{local_bin}:{os.environ['PATH']}"
        
    print(f"Starting VietTTS server on port {VIET_TTS_PORT} with 2 workers...")
    
    # Capture logs to a file for the UI to read
    with open("viettts_server.log", "w") as f:
        f.write("--- Server Start ---\n")
        
    log_file = open("viettts_server.log", "a")
    tts_process = subprocess.Popen(
        ["python3", "-c", "from viettts.cli import cli; cli()", "server", "--host", "0.0.0.0", "--port", str(VIET_TTS_PORT), "--workers", "2"],
        env=os.environ,
        stdout=log_file,
        stderr=log_file
    )

@atexit.register
def cleanup():
    if tts_process:
        tts_process.kill()
    os.system("pkill -9 -f viettts")

@app.post("/api/restart")
def restart_server():
    start_viettts()
    return {"status": "restarting"}

@app.get("/api/status")
def status():
    return {"ready": is_server_ready()}

@app.get("/api/logs")
def get_logs():
    if os.path.exists("viettts_server.log"):
        with open("viettts_server.log", "r") as f:
            lines = f.readlines()
            return {"logs": "".join(lines[-25:])}
    return {"logs": "No logs found."}

HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>VietTTS Reader</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');

:root {
  --bg: #0f172a;
  --panel: rgba(30, 41, 59, 0.7);
  --primary: #3b82f6;
  --primary-hover: #60a5fa;
  --text: #f8fafc;
  --text-muted: #94a3b8;
  --success: #10b981;
  --danger: #ef4444;
  --border: rgba(255, 255, 255, 0.1);
}

body {
  margin: 0; padding: 2rem;
  background: var(--bg);
  background-image: radial-gradient(circle at 10% 20%, rgba(59, 130, 246, 0.15) 0%, transparent 40%),
                    radial-gradient(circle at 90% 80%, rgba(139, 92, 246, 0.15) 0%, transparent 40%);
  color: var(--text);
  font-family: 'Outfit', sans-serif;
  min-height: 100vh;
}

.container { max-width: 1200px; margin: 0 auto; display: grid; grid-template-columns: 3fr 1fr; gap: 2rem; }
@media (max-width: 768px) { .container { grid-template-columns: 1fr; } }

h1 {
  font-size: 2.5rem; font-weight: 700; margin-bottom: 2rem;
  background: linear-gradient(to right, #60a5fa, #a78bfa);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  display: flex; align-items: center; gap: 1rem;
}

.panel {
  border: 1px solid var(--border); border-radius: 16px; padding: 1.5rem;
  backdrop-filter: blur(12px); background: var(--panel); box-shadow: 0 4px 24px rgba(0,0,0,0.2);
}

textarea {
  width: 100%; height: 500px; background: rgba(15, 23, 42, 0.6);
  border: 1px solid var(--border); border-radius: 12px; color: var(--text);
  padding: 1.5rem; font-family: inherit; font-size: 1rem; resize: vertical;
  outline: none; transition: border-color 0.3s; box-sizing: border-box; line-height: 1.6;
}
textarea:focus { border-color: var(--primary); }

.controls { display: flex; flex-direction: column; gap: 1.5rem; }

.status-badge {
  display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem;
  border-radius: 999px; background: rgba(0,0,0,0.3); border: 1px solid var(--border);
  font-weight: 600; font-size: 0.875rem; transition: all 0.3s;
}
.status-badge.online .dot { width: 10px; height: 10px; border-radius: 50%; background: var(--success); box-shadow: 0 0 10px var(--success); }
.status-badge.offline .dot { width: 10px; height: 10px; border-radius: 50%; background: var(--danger); box-shadow: 0 0 10px var(--danger); }

button {
  background: var(--primary); color: white; border: none; padding: 1rem;
  border-radius: 12px; font-weight: 600; font-size: 1.1rem; cursor: pointer;
  transition: all 0.2s; font-family: inherit; display: flex; justify-content: center;
  align-items: center; gap: 0.5rem;
}
button:hover:not(:disabled) { background: var(--primary-hover); transform: translateY(-2px); }
button:disabled { opacity: 0.5; cursor: not-allowed; }
button.secondary { background: rgba(255,255,255,0.1); font-size: 0.95rem; padding: 0.5rem 1rem; }
button.secondary:hover:not(:disabled) { background: rgba(255,255,255,0.2); }

.slider-group { display: flex; flex-direction: column; gap: 0.5rem; }
.slider-group label { display: flex; justify-content: space-between; font-size: 0.9rem; color: var(--text-muted); }
input[type="range"] { accent-color: var(--primary); }

.chunk-list { display: flex; flex-direction: column; gap: 1rem; margin-top: 1rem; max-height: 400px; overflow-y: auto; padding-right: 0.5rem; }
.chunk-item { background: rgba(255,255,255,0.05); border: 1px solid var(--border); border-radius: 12px; padding: 1rem; display: flex; flex-direction: column; gap: 0.5rem; animation: fadeIn 0.5s ease-out; }
.chunk-header { display: flex; justify-content: space-between; font-size: 0.85rem; color: var(--text-muted); }
audio { width: 100%; height: 36px; outline: none; }

.tech-details { margin-top: 2rem; }
.tech-details details { background: var(--panel); border: 1px solid var(--border); border-radius: 12px; padding: 1rem; }
.tech-details summary { cursor: pointer; font-weight: 600; color: var(--text-muted); user-select: none; }
.log-panel { margin-top: 1rem; font-family: monospace; background: rgba(0,0,0,0.5); padding: 1rem; border-radius: 8px; height: 200px; overflow-y: auto; color: var(--text-muted); font-size: 0.85rem; border: 1px solid var(--border); white-space: pre-wrap; }

.progress-container { margin-top: 0.5rem; display: none; }
.progress-bar { height: 6px; background: rgba(255,255,255,0.1); border-radius: 3px; overflow: hidden; margin-bottom: 0.5rem;}
.progress-fill { height: 100%; background: var(--primary); width: 0%; transition: width 0.3s; }
.progress-text { font-size: 0.85rem; color: var(--text-muted); text-align: center; }

@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
.spinner { width: 18px; height: 18px; border: 3px solid rgba(255,255,255,0.3); border-radius: 50%; border-top-color: white; animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.2); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.3); }
</style>
</head>
<body>

<div class="container">
    <div class="main-content panel">
        <h1>🗣️ Vietnamese TTS Reader</h1>
        <textarea id="input-text" placeholder="Paste your full Vietnamese chapter here... (Optimized for 16-20K chars)"></textarea>
        
        <div class="tech-details">
            <details>
                <summary>🛠️ Technical Details / Full Error Report</summary>
                <div class="log-panel" id="log"></div>
            </details>
        </div>
    </div>
    
    <div class="sidebar">
        <div class="panel controls">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div id="status-badge" class="status-badge offline"><div class="dot"></div><span id="status-text">Checking...</span></div>
                <button class="secondary" id="btn-restart" onclick="restartServer()">🔄 Restart</button>
            </div>
            
            <div class="slider-group" style="margin-bottom: 0.5rem;">
                <label><span>🗣️ Voice</span></label>
                <select id="voice-select" style="padding: 0.8rem; background: rgba(15, 23, 42, 0.6); color: var(--text); border: 1px solid var(--border); border-radius: 12px; font-family: inherit; font-size: 0.95rem; outline: none; transition: border-color 0.3s; width: 100%; cursor: pointer;">
                    <option value="nu-nhe-nhang" selected>Nữ Nhẹ Nhàng (Female)</option>
                    <option value="quynh">Quỳnh (Female)</option>
                    <option value="nguyen-ngoc-ngan">Nguyễn Ngọc Ngạn (Male)</option>
                </select>
            </div>

            <div class="slider-group">
                <label><span>⚡ Speed</span> <span id="speed-val">1.0x</span></label>
                <input type="range" id="speed" min="0.5" max="2.0" step="0.1" value="1.0" oninput="document.getElementById('speed-val').textContent = this.value + 'x'">
            </div>
            
            <button id="btn-read" onclick="startReading()" disabled>🎤 Read Aloud</button>

            <div class="progress-container" id="progress-container">
                <div class="progress-bar"><div class="progress-fill" id="progress-fill"></div></div>
                <div class="progress-text" id="progress-text">Progress: 0/0</div>
            </div>

            <div id="startup-logs" style="display:none; font-family: monospace; font-size: 0.75rem; background: rgba(0,0,0,0.3); padding: 0.8rem; border-radius: 8px; border: 1px solid var(--border); max-height: 150px; overflow-y: auto; margin-top: 1rem; color: #a5f3fc;">
                <div style="font-weight: 600; margin-bottom: 4px; color: var(--text-muted);">🛰️ Startup Feed:</div>
                <div id="startup-log-content" style="white-space: pre-wrap;">Initializing...</div>
            </div>

            <div class="chunk-list" id="chunk-list">
                <div style="text-align: center; color: var(--text-muted); font-size: 0.9rem; padding: 2rem 0;">
                    *Audio will appear here chunk-by-chunk...*
                </div>
            </div>
        </div>
    </div>
</div>

<script>
let currentChunks = [];
let audioQueue = [];
let synthesizedCount = 0;
let isPlaying = false;
let chunkTimers = {};
let overallTimer = null;
let synthesisStartTime = null;

function updateOverallProgress() {
    if(!synthesisStartTime) return;
    const elapsed = Math.floor((Date.now() - synthesisStartTime) / 1000);
    const m = Math.floor(elapsed / 60);
    const s = elapsed % 60;
    const timeStr = m > 0 ? `${m}m ${s}s` : `${s}s`;
    
    const progressText = document.getElementById('progress-text');
    if(progressText) {
        progressText.innerHTML = `Progress: ${synthesizedCount}/${currentChunks.length} <span style="margin-left:8px; color:var(--primary); font-weight:600">⏱️ Elapsed: ${timeStr}</span>`;
    }
}

function logMessage(msg) {
    const logEl = document.getElementById('log');
    logEl.textContent += `[${new Date().toLocaleTimeString()}] ${msg}\n`;
    logEl.scrollTop = logEl.scrollHeight;
}

let voicesLoaded = false;
async function loadVoices() {
    if(voicesLoaded) return;
    try {
        const res = await fetch('http://localhost:8298/v1/voices');
        if (res.ok) {
            const voices = await res.json();
            const select = document.getElementById('voice-select');
            const currentVal = select.value;
            select.innerHTML = '';
            voices.forEach(v => {
                const opt = document.createElement('option');
                opt.value = v;
                let label = v;
                if(v === 'nguyen-ngoc-ngan') label = 'Nguyễn Ngọc Ngạn (Male)';
                else if(v.includes('nu-nhe-nhang')) label = 'Nữ Nhẹ Nhàng (Female)';
                else if(v.includes('quynh')) label = 'Quỳnh (Female)';
                else if(v.includes('speechify_11') || v.includes('speechify_12')) label = v + ' (Female)';
                else if(v.includes('cdteam') || v.includes('atuan')) label = v + ' (Male)';
                opt.textContent = label;
                select.appendChild(opt);
            });
            if(voices.includes(currentVal)) select.value = currentVal;
            voicesLoaded = true;
        }
    } catch(e) {}
}

async function checkStatus() {
    try {
        const res = await fetch('/api/status');
        const data = await res.json();
        const badge = document.getElementById('status-badge');
        const text = document.getElementById('status-text');
        const startupLogs = document.getElementById('startup-logs');
        
        if (data.ready) {
            badge.className = 'status-badge online';
            text.textContent = 'Server Online';
            startupLogs.style.display = 'none';
            loadVoices();
            if(!isPlaying && synthesizedCount === (currentChunks.length || 0)) {
                // Keep enabled if we are idle and server is ready
                document.getElementById('btn-read').disabled = false;
            }
        } else {
            badge.className = 'status-badge offline';
            text.textContent = 'Server Offline';
            document.getElementById('btn-read').disabled = true;
            
            // Fetch live startup logs
            startupLogs.style.display = 'block';
            try {
                const lRes = await fetch('/api/logs');
                const lData = await lRes.json();
                const content = document.getElementById('startup-log-content');
                if(content.textContent !== lData.logs) {
                    content.textContent = lData.logs;
                    content.parentElement.scrollTop = content.parentElement.scrollHeight;
                }
            } catch(e){}
        }
    } catch(e) {
        document.getElementById('status-badge').className = 'status-badge offline';
        document.getElementById('status-text').textContent = 'Unreachable';
        document.getElementById('btn-read').disabled = true;
    }
}

setInterval(checkStatus, 2000);
checkStatus();

async function restartServer() {
    const btn = document.getElementById('btn-restart');
    btn.disabled = true;
    btn.innerHTML = `<div class="spinner"></div>`;
    logMessage("Restarting backend server...");
    document.getElementById('status-badge').className = 'status-badge offline';
    document.getElementById('status-text').textContent = 'Restarting...';
    document.getElementById('btn-read').disabled = true;
    
    try { await fetch('/api/restart', {method: 'POST'}); } catch(e){}
    
    let attempts = 0;
    while (attempts < 60) {
        try {
            const res = await fetch('/api/status');
            const data = await res.json();
            if(data.ready) break;
        } catch(e){}
        await new Promise(r => setTimeout(r, 1000));
        attempts++;
        if (attempts % 5 === 0) logMessage(`Waiting for model reload... (${attempts}s)`);
    }
    btn.disabled = false;
    btn.innerHTML = `🔄 Restart`;
    checkStatus();
    logMessage("Backend server restarted.");
}

function smartSplit(text, maxChars = 2000) {
    const sentences = text.match(/[^.!?\\n]+[.!?\\n]*\\s*/g) || [text];
    const chunks = [];
    let current = "";
    let isFirstChunk = true;

    for (let sent of sentences) {
        let targetLimit = isFirstChunk ? 250 : maxChars;
        if (sent.length > targetLimit) {
            if (current.trim()) { chunks.push(current.trim()); isFirstChunk = false; current = ""; targetLimit = maxChars; }
            const words = sent.split(/\\s+/);
            let tempChunk = "";
            for (let word of words) {
                if (word.length > targetLimit) {
                    if (tempChunk.trim()) { chunks.push(tempChunk.trim()); isFirstChunk = false; targetLimit = maxChars; tempChunk = ""; }
                    for (let i = 0; i < word.length; i += targetLimit) {
                        chunks.push(word.substring(i, i + targetLimit));
                        isFirstChunk = false; targetLimit = maxChars;
                    }
                } else if ((tempChunk + word).length < targetLimit) {
                    tempChunk += word + " ";
                } else {
                    chunks.push(tempChunk.trim());
                    isFirstChunk = false; targetLimit = maxChars;
                    tempChunk = word + " ";
                }
            }
            current = tempChunk;
        } else if ((current + sent).trim().length < targetLimit) {
            current += sent + " ";
        } else {
            chunks.push(current.trim());
            isFirstChunk = false; current = sent + " ";
        }
    }
    if (current.trim()) { chunks.push(current.trim()); }
    return chunks;
}

async function synthChunk(index, text, speed) {
    const voiceId = document.getElementById('voice-select') ? document.getElementById('voice-select').value : 'nu-nhe-nhang';
    const response = await fetch('http://localhost:8298/v1/audio/speech', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            input: text,
            model: 'tts-1',
            voice: voiceId,
            response_format: 'wav',
            speed: parseFloat(speed)
        })
    });
    
    if(!response.ok) {
        const err = await response.text();
        throw new Error(`HTTP ${response.status}: ${err}`);
    }
    const blob = await response.blob();
    return URL.createObjectURL(blob);
}

function playNextAudio() {
    if(audioQueue.length === 0) { isPlaying = false; return; }
    
    const nextIdx = audioQueue.findIndex(a => !a.played);
    if(nextIdx !== -1) {
        isPlaying = true;
        const chunkState = audioQueue[nextIdx];
        chunkState.played = true;
        
        // Ensure active chunk is visible
        const chunkItem = document.getElementById(`chunk-item-${chunkState.index}`);
        if(chunkItem) chunkItem.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        
        const audioEl = document.getElementById(`audio-${chunkState.index}`);
        logMessage(`Playing part ${chunkState.index + 1}...`);
        
        audioEl.play().catch(e => {
            logMessage(`Autoplay prevented for part ${chunkState.index+1}. User interaction required.`);
        });
        
    } else {
        isPlaying = false;
        logMessage("Finished reading all parts.");
        if (synthesizedCount === currentChunks.length) {
            document.getElementById('btn-read').innerHTML = `🎤 Read Aloud`;
            document.getElementById('btn-read').disabled = false;
        }
    }
}

async function startReading() {
    const text = document.getElementById('input-text').value.trim();
    if(!text) { alert("Please enter text."); return; }
    
    const speed = document.getElementById('speed').value;
    const btn = document.getElementById('btn-read');
    btn.disabled = true;
    btn.innerHTML = `<div class="spinner"></div>`;
    
    document.getElementById('chunk-list').innerHTML = '';
    document.getElementById('log').textContent = '';
    
    if (audioQueue.length > 0) {
        audioQueue.forEach(a => URL.revokeObjectURL(a.url));
    }
    
    logMessage("Started smart splitting...");
    const chunks = smartSplit(text);
    logMessage(`Splitted into ${chunks.length} parts.`);
    currentChunks = chunks;
    audioQueue = [];
    synthesizedCount = 0;
    isPlaying = false;
    
    Object.keys(chunkTimers).forEach(k => clearInterval(chunkTimers[k].interval));
    chunkTimers = {};
    if(overallTimer) clearInterval(overallTimer);
    synthesisStartTime = Date.now();
    updateOverallProgress();
    overallTimer = setInterval(updateOverallProgress, 1000);
    
    document.getElementById('progress-container').style.display = 'block';
    document.getElementById('progress-fill').style.width = '0%';
    
    try {
        logMessage("Synthesizing part 1 (FAST START)...");
        createAudioUI(0);
        const url = await synthChunk(0, chunks[0], speed);
        handleChunkReady(0, url);
        
        btn.innerHTML = `🎤 Processing...`;
        
        if(chunks.length > 1) {
            processBackgroundChunks(chunks.slice(1), speed);
        } else {
            logMessage("All parts completed.");
            btn.innerHTML = `🎤 Read Aloud`;
            btn.disabled = false;
        }
    } catch(e) {
        logMessage(`Error synthesizing part 1: ${e.message}`);
        if(chunkTimers[0]) clearInterval(chunkTimers[0].interval);
        document.getElementById(`chunk-status-0`).textContent = '❌ Error';
        btn.innerHTML = `🎤 Read Aloud`;
        btn.disabled = false;
    }
}

function createAudioUI(index) {
    const list = document.getElementById('chunk-list');
    const div = document.createElement('div');
    div.className = 'chunk-item';
    div.id = `chunk-item-${index}`;
    div.innerHTML = `
        <div class="chunk-header">
            <span>▶️ Part ${index + 1}</span>
            <span id="chunk-status-${index}">⏳ Synthing... 0s</span>
        </div>
        <audio id="audio-${index}" controls></audio>
    `;
    list.appendChild(div);
    
    const charCount = currentChunks[index] ? currentChunks[index].length : 0;
    // Updated based on user hardware telemetry (~1.8 seconds per character processing time on CPU base load)
    const estTimeSecs = Math.max(180, Math.floor(charCount * 1.8));
    
    chunkTimers[index] = {
        start: Date.now(),
        interval: setInterval(() => {
            const el = document.getElementById(`chunk-status-${index}`);
            if (el && el.textContent.includes('Synthing')) {
                const elapsed = Math.floor((Date.now() - chunkTimers[index].start) / 1000);
                const m = Math.floor(elapsed / 60);
                const s = elapsed % 60;
                const t = m > 0 ? `${m}m ${s}s` : `${s}s`;
                
                const remaining = Math.max(0, estTimeSecs - elapsed);
                const rm = Math.floor(remaining / 60);
                const rs = remaining % 60;
                const rt = rm > 0 ? `~${rm}m ${rs}s left` : `~${rs}s left`;
                
                if (elapsed >= estTimeSecs) {
                    el.innerHTML = `⏳ Synthing... <b>${t}</b> <span style="font-size:0.85em; color:var(--text-muted); font-weight:normal; margin-left:4px">(finishing up...)</span>`;
                } else {
                    el.innerHTML = `⏳ Synthing... <b>${t}</b> <span style="font-size:0.85em; color:var(--text-muted); font-weight:normal; margin-left:4px">(${rt})</span>`;
                }
            } else {
                if(chunkTimers[index]) clearInterval(chunkTimers[index].interval);
            }
        }, 1000)
    };
}

function handleChunkReady(index, url) {
    const audioEl = document.getElementById(`audio-${index}`);
    audioEl.src = url;
    
    if(chunkTimers[index]) clearInterval(chunkTimers[index].interval);
    const elapsed = Math.floor((Date.now() - chunkTimers[index].start) / 1000);
    const m = Math.floor(elapsed / 60);
    const s = elapsed % 60;
    const t = m > 0 ? `${m}m ${s}s` : `${s}s`;
    
    document.getElementById(`chunk-status-${index}`).innerHTML = `✅ Ready <i>(${t})</i>`;
    
    audioEl.addEventListener('ended', playNextAudio);
    
    audioQueue.push({index, url, played: false});
    audioQueue.sort((a,b) => a.index - b.index);
    
    synthesizedCount++;
    document.getElementById('progress-fill').style.width = `${(synthesizedCount / currentChunks.length) * 100}%`;
    updateOverallProgress();
    if(synthesizedCount === currentChunks.length && overallTimer) {
        clearInterval(overallTimer);
        overallTimer = null;
    }
    logMessage(`Part ${index + 1} ready.`);
    
    if(!isPlaying) {
        playNextAudio();
    }
}

async function processBackgroundChunks(chunks, speed) {
    let queue = chunks.map((text, i) => ({index: i + 1, text}));
    
    async function worker() {
        while(queue.length > 0) {
            const task = queue.shift();
            createAudioUI(task.index);
            try {
                const url = await synthChunk(task.index, task.text, speed);
                handleChunkReady(task.index, url);
            } catch(e) {
                logMessage(`Error in part ${task.index + 1}: ${e.message}`);
                if(chunkTimers[task.index]) clearInterval(chunkTimers[task.index].interval);
                document.getElementById(`chunk-status-${task.index}`).textContent = '❌ Error';
            }
        }
    }
    
    await Promise.all([worker(), worker()]);
    logMessage("All background parts completed.");
    
    if (!isPlaying && synthesizedCount === currentChunks.length) {
        document.getElementById('btn-read').innerHTML = `🎤 Read Aloud`;
        document.getElementById('btn-read').disabled = false;
    }
}
</script>
</body>
</html>
"""

@app.get("/")
def read_root():
    return HTMLResponse(content=HTML_CONTENT)

def main():
    start_viettts()
    
    config = uvicorn.Config(app, host="0.0.0.0", port=UI_PORT, log_level="error")
    server = uvicorn.Server(config)
    
    # Disable Uvicorn's default signal handlers to prevent hanging on graceful shutdown
    server.install_signal_handlers = lambda: None
    
    import signal
    import sys
    
    def force_exit(signum, frame):
        print("\n[VietTTS] Shutting down UI and background servers immediately...")
        if tts_process:
            try:
                tts_process.kill()
            except Exception:
                pass
        os.system("pkill -9 -f viettts")
        os._exit(0)
        
    signal.signal(signal.SIGINT, force_exit)
    signal.signal(signal.SIGTERM, force_exit)
    
    try:
        server.run()
    finally:
        # Guarantee cleanup even if uvicorn throws an exception (e.g. OSError port in use)
        if tts_process:
            try:
                tts_process.kill()
            except Exception:
                pass
        os.system("pkill -9 -f viettts")

if __name__ == "__main__":
    main()
