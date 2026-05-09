import ollama
import json
import time
from typing import Dict, List, Optional
from pydantic import BaseModel
from .history_manager import HistoryManager

class CaptionResponse(BaseModel):
    """Structured output for meme captions"""
    top: str
    bottom: str

class OllamaCaptioner:
    def __init__(self, model_name: str = "gemma-custom"):
        self.model_name = model_name
        self.history_manager = HistoryManager()
        
    def _build_system_prompt(self) -> str:
        return """You are an expert meme caption writer. Create funny, concise, classic-style meme text.
Rules:
- Top text: Setup or situation (short, punchy, 3-10 words)
- Bottom text: Punchline or twist (hilarious payoff, 5-15 words)
- Use internet meme humor style (ironic, relatable, absurd)
- NEVER add explanations, quotes, or extra text. Return ONLY valid JSON."""

    def _build_user_prompt(self, context: str, recent_history: List[Dict], template_id: Optional[str] = None) -> str:
        prompt = f"Context: {context}\n"
        if template_id:
            prompt += f"Template theme: {template_id}\n"
        
        if recent_history:
            prompt += "\nRecent memes (avoid repeating similar jokes):\n"
            for h in recent_history:
                prompt += f"- Top: {h.get('top_text', '')} | Bottom: {h.get('bottom_text', '')}\n"
        
        prompt += "\nGenerate ONE new funny meme caption. Respond with valid JSON ONLY: {\"top\": \"...\", \"bottom\": \"...\"}"
        return prompt

    def generate_caption(self, context: str = "general humor", template_id: Optional[str] = None) -> Dict:
        """Generate top and bottom text using Ollama with structured JSON output."""
        start_time = time.time()
        
        recent_history = self.history_manager.get_recent_history(limit=4)
        
        messages = [
            {"role": "system", "content": self._build_system_prompt()},
            {"role": "user", "content": self._build_user_prompt(context, recent_history, template_id)}
        ]
        
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=messages,
                format="json",
                options={"temperature": 0.85, "num_ctx": 4096}
            )
            
            content = response['message']['content'].strip()
            parsed = json.loads(content)
            caption = CaptionResponse.model_validate(parsed)
            
            print(f"✅ LLM Caption generated in {time.time() - start_time:.2f}s")
            return {"top": caption.top.strip(), "bottom": caption.bottom.strip()}
            
        except Exception as e:
            print(f"⚠️ LLM Error: {e}. Using fallback caption...")
            return {
                "top": f"{context[:25].upper()}",
                "bottom": "YOU WON'T BELIEVE WHAT HAPPENS NEXT"
            }

    def close(self):
        self.history_manager.close()