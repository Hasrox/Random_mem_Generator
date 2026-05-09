# Adaptive Local Meme Generator — Phase 0

## Quick Start (RTX 4080)
```bash
conda create -n meme_generator python=3.11 -y
conda activate meme_generator
cd meme_generator
pip install -r requirements.txt

# Ollama model (one-time)
ollama pull hf.co/OBLITERATUS/gemma-4-E4B-it-OBLITERATED:Q5_K_M
# (fallback will be pulled automatically later)

# Place your assets
# assets/templates/  ← your 50+ PNG/JPG files
# assets/sfx/        ← your 30+ audio files

python main.py
# or launch Gradio later: python gradio_app.py