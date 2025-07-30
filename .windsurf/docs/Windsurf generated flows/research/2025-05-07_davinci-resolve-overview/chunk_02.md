# AI Features in DaVinci Resolve (Free & Studio)

## Built-in AI Tools (Free & Studio)
- **Magicut:** Smart scene detection and auto-editing.
- **Voice Isolation:** Removes background noise from dialogue.
- **Smart Reframe:** Automatically reframes video for different aspect ratios (social, vertical, etc.).
- **Objectracking:** Tracks faces and objects for color grading/effects.

## Studio-Only Advanced AI
- **Magic Mask:** AI-powered subject/area masking for color/VFX.
- **Super Scale:** AI upscaling for low-res footage.
- **Advanced Noise Reduction:** Temporal & spatial noise removal.
- **AI-basedeinterlacing, Face Refinement, and more.**

## Scripting & Custom AI
- **Python/Lua scripting lets you:**
  - Automate repetitivediting tasks.
  - Build custom batch workflows (e.g., batch render, batch color match).
  - Integrate with external AI tools (e.g., call outo Python ML models for scene detection, tagging, etc. — then update timeline/metadata).
- **Custom AI plugins:**
  - Advanced users can build OpenFX plugins (C++/CUDA/Metal) to add their own AI-powered effects or processing.

## Example AI Workflows You Could Build
- **Auto-tagging:** Use Python to analyze imported video/audio, call external AI for tagging (e.g., face recognition, speech-to-text), and write results into Resolve’s metadata.
- **Batch Smart Editing:** Script Magicut or scene detection across dozens of clips for automated rough cuts.
- **AI-driven Color Matching:** Integrate with external color analysis tools for consistent grading.
- **Voice-to-Subtitle:** Usexternal ASR (automatic speech recognition) to generate subtitles, then import into timeline.
- **Custom Effects:** Build OpenFX plugins that use AI for style transfer, denoising, or other creativeffects.

---

**Most AI scripting and automation is possible in the free version. Studio unlocks more built-in AI tools and higher-end processing.**
