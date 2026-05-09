import gradio as gr
from core.asset_manager import AssetManager
from core.history_manager import HistoryManager
from core.llm_captioner import OllamaCaptioner
from core.meme_composer import MemeComposer
from pathlib import Path
import random

# Global singletons for performance
am = AssetManager()
hm = HistoryManager()
captioner = OllamaCaptioner(model_name="gemma-custom")
composer = MemeComposer()


def generate_meme(context: str, system_prompt: str):
    """Full pipeline called by Gradio buttons."""
    if not context.strip():
        context = "random funny situation"
    
    # 1. Assets
    template_path, template_id = am.get_weighted_template()
    sfx_path, sfx_id = am.get_weighted_sfx()
    
    # 2. LLM Caption — now supports custom system prompt
    caption = captioner.generate_caption(
        context=context, 
        template_id=template_id,
        system_prompt=system_prompt if system_prompt and system_prompt.strip() else None
    )
    
    # 3. Compose meme
    meme_path = composer.compose_and_play(
        template_path=template_path,
        top_text=caption["top"],
        bottom_text=caption["bottom"],
        sfx_path=sfx_path,
        context=context
    )
    
    # 4. Record history
    hm.record_generation(
        template_id=template_id,
        sfx_id=sfx_id,
        context=context,
        top=caption["top"],
        bottom=caption["bottom"]
    )
    
    return meme_path, sfx_path, caption["top"], caption["bottom"]


def get_history_gallery():
    try:
        records = hm.get_recent_history(limit=20)
        if not records:
            return [], "No memes generated yet. Generate some in the first tab! 🎉"
        
        captions = []
        for r in records:
            caption_str = f"Top: {r.get('top_text','')}\nBottom: {r.get('bottom_text','')}\nContext: {r.get('context','')}"
            captions.append(caption_str)
        
        return [], "\n\n".join([f"#{i+1} {c}" for i, c in enumerate(captions)])
    except Exception as e:
        return [], f"History unavailable: {e}"


def random_context():
    random_prompts = [
        "toilet humor", "Monday morning at work", "relationship drama",
        "existential dread", "student loan debt", "forever alone", "winter is coming",
        "cat meme energy", "gaming rage", "office coffee addiction"
    ]
    return random.choice(random_prompts)


# ==================== DARK-OPTIMIZED THEME ====================
dark_theme = gr.themes.Default(
    primary_hue="orange",
    secondary_hue="blue",
    neutral_hue="zinc",
    text_size="lg",
    spacing_size="md",
    radius_size="lg",
).set(
    body_background_fill_dark="#0a0a0a",
    block_background_fill_dark="#1a1a1a",
    block_border_color_dark="#333333",
    button_primary_background_fill_dark="#f97316",
    button_primary_background_fill_hover_dark="#fb923c",
    button_primary_text_color_dark="#ffffff",
    input_background_fill_dark="#262626",
    input_border_color_dark="#525252",
    slider_color_dark="#f97316",
    checkbox_label_background_fill_dark="#1a1a1a",
)

css = """
.gradio-container { max-width: 1280px; margin: auto; }
.gr-image { background: #111; border-radius: 12px; }
"""

# ==================== UI ====================
with gr.Blocks(title="Adaptive Local Meme Generator") as demo:
    
    gr.Markdown("# 🚀 Adaptive Local Meme Generator\n**Phase 0 Complete** — 100% local, GPU-fast, classic memes")
    
    with gr.Tabs():
        with gr.Tab("🔥 Generate Meme"):
            with gr.Row():
                with gr.Column(scale=3):
                    context_input = gr.Textbox(
                        label="🎯 Your Meme Context / Prompt",
                        placeholder="e.g. Monday morning at work, toilet humor...",
                        lines=3,
                        max_lines=5
                    )
                    # === NEW: Custom System Prompt UI ===
                    with gr.Accordion("⚙️ Advanced: Custom LLM System Prompt (empty = default)", open=False):
                        system_prompt_input = gr.Textbox(
                            label="System Prompt",
                            placeholder="Paste your custom system prompt here...\n(leave empty to use default from llm_captioner.py)",
                            lines=6,
                            value=""
                        )
                    
                    with gr.Row():
                        generate_btn = gr.Button("🔥 Generate Meme", variant="primary", size="large")
                        regenerate_btn = gr.Button("🔄 Regenerate (keep context)", variant="secondary", size="large")
                        random_btn = gr.Button("🎲 Random Context", variant="secondary", size="large")
                
                with gr.Column(scale=7):
                    output_image = gr.Image(label="🖼️ Your Meme", height=620)
                    output_audio = gr.Audio(label="🔊 Sound Effect", type="filepath")
            
            with gr.Row():
                top_text = gr.Textbox(label="Top Text", interactive=False)
                bottom_text = gr.Textbox(label="Bottom Text", interactive=False)
        
        with gr.Tab("📜 History Gallery"):
            history_output = gr.Textbox(label="Recent Memes", lines=15, interactive=False)
            refresh_btn = gr.Button("🔄 Refresh History", size="small")
    
    # Button actions
    generate_btn.click(
        fn=generate_meme,
        inputs=[context_input, system_prompt_input],
        outputs=[output_image, output_audio, top_text, bottom_text]
    )
    
    regenerate_btn.click(
        fn=generate_meme,
        inputs=[context_input, system_prompt_input],
        outputs=[output_image, output_audio, top_text, bottom_text]
    )
    
    random_btn.click(fn=random_context, outputs=context_input)
    
    def refresh_history():
        _, status_text = get_history_gallery()
        return status_text
    
    refresh_btn.click(fn=refresh_history, outputs=history_output)
    demo.load(fn=refresh_history, outputs=history_output)

if __name__ == "__main__":
    print("🚀 Launching Adaptive Local Meme Generator on port 8087...")
    demo.launch(
        server_name="127.0.0.1",
        server_port=8087,
        share=False,
        show_error=True,
        theme=dark_theme,
        css=css
    )
