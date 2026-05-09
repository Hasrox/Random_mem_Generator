import gradio as gr
from core.asset_manager import AssetManager
from core.history_manager import HistoryManager
from core.llm_captioner import OllamaCaptioner
from core.meme_composer import MemeComposer
from pathlib import Path

# Global singletons for performance
am = AssetManager()
hm = HistoryManager()
captioner = OllamaCaptioner(model_name="gemma-custom")
composer = MemeComposer()


def generate_meme(context: str):
    """Full pipeline called by Gradio button."""
    if not context.strip():
        context = "random funny situation"
    
    # 1. Assets
    template_path, template_id = am.get_weighted_template()
    sfx_path, sfx_id = am.get_weighted_sfx()
    
    # 2. LLM Caption
    caption = captioner.generate_caption(context=context, template_id=template_id)
    
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
    
    # Return for Gradio: image path, audio path, top text, bottom text
    return meme_path, sfx_path, caption["top"], caption["bottom"]


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

# Gradio UI
with gr.Blocks(
    title="Adaptive Local Meme Generator",
    theme=dark_theme,
    css="""
    .gradio-container { max-width: 1200px; margin: auto; }
    .gr-image { background: #111; }
    """
) as demo:
    
    gr.Markdown("# 🚀 Adaptive Local Meme Generator\n**Phase 0 Complete** — 100% local, GPU-fast, classic memes")
    
    with gr.Row():
        with gr.Column(scale=3):
            context_input = gr.Textbox(
                label="🎯 Your Meme Context / Prompt",
                placeholder="e.g. Monday morning at work, toilet humor, relationship drama...",
                lines=3,
                max_lines=5
            )
            with gr.Row():
                generate_btn = gr.Button("🔥 Generate Meme", variant="primary", size="large")
                regenerate_btn = gr.Button("🔄 Regenerate", variant="secondary", size="large")
        
        with gr.Column(scale=7):
            output_image = gr.Image(
                label="🖼️ Your Meme",
                height=620,
                show_download_button=True
            )
            output_audio = gr.Audio(
                label="🔊 Sound Effect",
                type="filepath",
                show_download_button=True
            )
    
    with gr.Row():
        top_text = gr.Textbox(label="Top Text", interactive=False)
        bottom_text = gr.Textbox(label="Bottom Text", interactive=False)
    
    # Button actions
    generate_btn.click(
        fn=generate_meme,
        inputs=context_input,
        outputs=[output_image, output_audio, top_text, bottom_text]
    )
    
    regenerate_btn.click(
        fn=generate_meme,
        inputs=context_input,
        outputs=[output_image, output_audio, top_text, bottom_text]
    )
    
    gr.Markdown("""
    ### 💾 Memes are automatically saved to `generated_memes/`  
    History is stored in SQLite for future adaptive phases.
    """)

if __name__ == "__main__":
    print("🚀 Launching Adaptive Local Meme Generator...")
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        show_error=True,
        favicon_path=None  # You can add a custom favicon later
    )
