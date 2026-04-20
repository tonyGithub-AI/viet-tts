# Agent Rules - Viet-TTS Project

This document outlines the rules and best practices for the AI Agent (Antigravity) working on the Viet-TTS project.

## Core Rules

1.  **Synchronization Rule**:
    - Every code change must be accompanied by corresponding updates to the PRD (`TTS_PRD.md`) and the relevant test files.
    - Conversely, any update to the PRD or tests must be reflected in the code implementation.
    - This ensures that the documentation, tests, and code remain in sync at all times.

2.  **Regression Testing Rule**:
    - Every change (code, documentation, or test) must trigger a full regression test of the system.
    - No changes should be finalized without verifying that existing functionality remains intact.

3.  **Gradio Compatibility**:
    - Ensure compatibility with Gradio 6.x.
    - Maintain the pattern of passing `theme` to `demo.launch()` rather than the `gr.Blocks` constructor.
    - Avoid using deprecated components like `gr.Separator()`.
