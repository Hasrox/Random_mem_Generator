from PIL import Image, ImageDraw, ImageFont
import pygame
from pathlib import Path
from datetime import datetime
import time
from typing import Dict, List, Optional

class MemeComposer:
    def __init__(self, output_dir: str = "generated_memes"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        # Initialize pygame mixer once
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        
    def _wrap_text(self, text: str, max_chars: int = 25) -> List[str]:
        """Word-aware wrapping at max 25 characters per line."""
        if not text:
            return [""]
        words = text.split()
        lines = []
        current_line = []
        for word in words:
            test_line = " ".join(current_line + [word])
            if len(test_line) <= max_chars:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
        if current_line:
            lines.append(" ".join(current_line))
        return lines

    def _get_font(self, size: int):
        """Classic meme font with graceful fallback."""
        try:
            # Try Impact first (classic meme font)
            font_path = Path("assets/impact.ttf")
            if font_path.exists():
                return ImageFont.truetype(str(font_path), size)
            # Common system fallbacks
            return ImageFont.truetype("arial.ttf", size)  # Windows/macOS
        except Exception:
            return ImageFont.load_default()  # Ultimate fallback

    def _draw_text_with_stroke(self, draw: ImageDraw.Draw, text: str, position: tuple, font: ImageFont, 
                               fill: str = "white", stroke_fill: str = "black", stroke_width: int = 4):
        """Draw text with black outline for classic meme look."""
        x, y = position
        for adj in range(-stroke_width, stroke_width + 1):
            for adj2 in range(-stroke_width, stroke_width + 1):
                draw.text((x + adj, y + adj2), text, font=font, fill=stroke_fill)
        draw.text((x, y), text, font=font, fill=fill)

        def _calculate_font_size(self, width: int, height: int, longest_line: str) -> int:
        """Highly dynamic font sizing that adapts perfectly to any template resolution."""
        min_dim = min(width, height)
        base_size = int(min_dim * 0.088)                    # ~8.8% of smallest dimension
        
        # Text length penalty (stronger for very long wrapped lines)
        length_factor = max(1.0, len(longest_line) / 19)
        size = int(base_size / length_factor)
        
        # Dynamic bounds that scale with the actual image size
        min_size = max(26, int(min_dim * 0.04))
        max_size = min(170, int(min_dim * 0.23))
        
        final_size = max(min_size, min(size, max_size))
        return final_size

    def compose_and_play(self, template_path: str, top_text: str, bottom_text: str, 
                        sfx_path: str, context: str = "") -> str:
        """Full meme composition with improved dynamic font scaling."""
        start_time = time.time()
        
        # 1. Load image
        img = Image.open(template_path).convert("RGB")
        draw = ImageDraw.Draw(img)
        width, height = img.size
        
        # 2. Wrap text (25 chars/line)
        top_lines = self._wrap_text(top_text)
        bottom_lines = self._wrap_text(bottom_text)
        
        # 3. Dynamic font sizing (now uses full image dimensions)
        all_lines = top_lines + bottom_lines
        longest_line = max(all_lines, key=len) if all_lines else ""
        font_size = self._calculate_font_size(width, height, longest_line)
        font = self._get_font(font_size)
        
        # ... (rest of the method unchanged — multi-line drawing, async audio, save, show, etc.)
        
        # 4. Draw top text (multi-line, centered)
        line_height = font_size * 1.1
        top_start_y = int(height * 0.08)
        for i, line in enumerate(top_lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            line_width = bbox[2] - bbox[0]
            x = (width - line_width) // 2
            y = top_start_y + (i * line_height)
            self._draw_text_with_stroke(draw, line, (x, y), font)
        
        # 5. Draw bottom text (multi-line, centered)
        bottom_start_y = height - int(height * 0.15) - (len(bottom_lines) * line_height)
        for i, line in enumerate(bottom_lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            line_width = bbox[2] - bbox[0]
            x = (width - line_width) // 2
            y = bottom_start_y + (i * line_height)
            self._draw_text_with_stroke(draw, line, (x, y), font)
        
        # 6. Save meme
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = self.output_dir / f"meme_{timestamp}.png"
        img.save(output_path)
        
        # 7. Async audio (fire-and-forget)
        try:
            pygame.mixer.music.load(sfx_path)
            pygame.mixer.music.play()
            print(f"🔊 Playing SFX (async): {Path(sfx_path).stem}")
        except Exception as e:
            print(f"⚠️ Audio playback skipped: {e}")
        
        # 8. Optional safe preview
        try:
            img.show()  # Windows-safe — no crash if viewer unavailable
        except Exception:
            pass
        
        print(f"✅ Meme composed and saved in {time.time() - start_time:.2f}s → {output_path}")
        return str(output_path)

    def close(self):
        pygame.mixer.quit()