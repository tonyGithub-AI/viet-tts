# Issue Tracking Log

This document tracks identified bugs, systemic issues, and technical debt items across the Viet-TTS project, alongside their resolution status.

## Current Outstanding Issues

_None explicitly identified at this moment._

## Resolved Issues

### Issue-2026-04-22-1: Errno 98 (Address already in use) Server Zombie Failure

- **Date Fixed**: April 22, 2026
- **Component**: UI Backend (`uvicorn` networking / Lifecycle Management)
- **Symptom**: Terminating `tts_web.py` via `Ctrl+C` or attempting to execute a background UI restart often left the app port (`7860`) or backend TTS process (`8298`) locked and hung. Any subsequent attempt to boot triggered a hard `OSError [Errno 98]`.
- **Resolution**:
  - Overrode the default graceful shutdown within Uvicorn's configuration.
  - Injected an absolute global `SIGINT/SIGTERM` signal trap that executes strict termination logic (`tts_process.kill()` + `os._exit(0)`).
  - Wrapped `server.run()` in a `try...finally` block within `main()` to guarantee aggressive background cleanups even on startup failures.

### Issue-2026-04-22-2: FFMPEG Broken Pipe Audio Interruptions

- **Date Fixed**: April 22, 2026
- **Component**: Audio synthesis / Web workers
- **Symptom**: "Error writing trailer: Broken pipe" crashes during sequential generation. These occur predominantly when background background tasks hit limits or during rapid termination.
- **Resolution**: Fixed underlying terminal threading overlaps using the port clearance above and enabling graceful cleanup on exception states.

---
