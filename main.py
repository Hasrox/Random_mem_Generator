from core.asset_manager import AssetManager
from core.history_manager import HistoryManager
from core.llm_captioner import OllamaCaptioner
from core.meme_composer import MemeComposer
import sys

if __name__ == "__main__":
    print("🚀 Adaptive Local Meme Generator — Milestone 3 Full Pipeline Test (PATCHED)")
    
    am = AssetManager()
    hm = HistoryManager()
    captioner = OllamaCaptioner(model_name="gemma-custom")
    composer = MemeComposer()
    
    try:
        # 1. Assets
        template_path, template_id = am.get_weighted_template()
        sfx_path, sfx_id = am.get_weighted_sfx()
        print(f"✅ Selected template: {template_id}")
        print(f"✅ Selected SFX: {sfx_id}")
        
        # 2. User context
        context = input("\nEnter meme context/prompt (or press Enter for random humor): ").strip()
        if not context:
            context = "random funny situation"
        
        # 3. LLM Caption
        print("🤖 Generating funny caption with Ollama...")
        caption = captioner.generate_caption(context=context, template_id=template_id)
        print(f"🎯 Top:    {caption['top']}")
        print(f"🎯 Bottom: {caption['bottom']}")
        
        # 4. Compose + Audio + Save (patched)
        print("\n🖼️  Composing meme with Pillow (25-char wrap + dynamic scaling)...")
        meme_path = composer.compose_and_play(
            template_path=template_path,
            top_text=caption['top'],
            bottom_text=caption['bottom'],
            sfx_path=sfx_path,
            context=context
        )
        
        # 5. Record to history
        hm.record_generation(
            template_id=template_id,
            sfx_id=sfx_id,
            context=context,
            top=caption['top'],
            bottom=caption['bottom']
        )
        
        print("\n🎉 FULL MEME GENERATED SUCCESSFULLY!")
        print(f"📁 Saved to: {meme_path}")
        print("✅ Milestone 3 patched and complete — ready for Gradio UI!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        am.close()
        hm.close()
        captioner.close()
        composer.close()