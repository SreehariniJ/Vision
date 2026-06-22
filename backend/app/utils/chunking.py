import re
from typing import List

def chunk_text(text: str, chunk_size: int = 4000, overlap: int = 200) -> List[str]:
    """
    Splits text into chunks of roughly `chunk_size` characters, 
    with an overlap of `overlap` characters to preserve context.
    Attempts to split on paragraph or sentence boundaries where possible.
    """
    if not text:
        return []

    # Simple normalization
    text = re.sub(r'\n{3,}', '\n\n', text).strip()
    
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = min(start + chunk_size, text_length)
        
        # If we are not at the end of the text, try to find a natural break
        if end < text_length:
            # Try to break at a double newline (paragraph)
            last_para = text.rfind('\n\n', start, end)
            if last_para != -1 and last_para > start + chunk_size // 2:
                end = last_para + 2
            else:
                # Try to break at a period/sentence boundary
                last_period = text.rfind('. ', start, end)
                if last_period != -1 and last_period > start + chunk_size // 2:
                    end = last_period + 2
                else:
                    # Fallback to nearest space
                    last_space = text.rfind(' ', start, end)
                    if last_space != -1 and last_space > start:
                        end = last_space + 1
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
            
        # Move start forward, accounting for overlap
        start = end - overlap
        # Prevent infinite loops if overlap is larger than forward progress
        if start <= chunks[-1] if chunks else 0: # Ensure we move forward
            start = end - (overlap // 2)

    return chunks
