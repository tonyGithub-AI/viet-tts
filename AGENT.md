# Agent Rules - Viet-TTS Project

This document outlines the rules and best practices for the AI Agent (Antigravity) working on the Viet-TTS project.

## Core Rules

1.  **Synchronization Rule**:
    - Every code change (including those made manually by the user or dynamically by the agent) _must_ be accompanied by corresponding updates to the PRD (`TTS_PRD.md`) and the relevant test files if it is not already documented.
    - Conversely, any update to the PRD or tests must be reflected in the code implementation.
    - **Explicit PRD Update Rule:** If any code changes are introduced that are not already in the PRD, you MUST update the PRD accordingly.
    - This ensures that the documentation, tests, and code remain in sync at all times.

2.  **Regression Testing Rule**:
    - Every change (code, documentation, or test) must trigger a full regression test of the system.
    - No changes should be finalized without verifying that existing functionality remains intact.

3.  **Gradio Compatibility**:
    - Ensure compatibility with Gradio 6.x.
    - Maintain the pattern of passing `theme` to `demo.launch()` rather than the `gr.Blocks` constructor.
    - Avoid using deprecated components like `gr.Separator()`.
