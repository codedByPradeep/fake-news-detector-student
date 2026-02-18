try:
    from transformers import pipeline
    _summarizer_pipeline = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6", framework="pt")  # Using a small, fast model
except ImportError:
    _summarizer_pipeline = None
except Exception as e:
    print(f"Warning: Could not load summarizer model: {e}")
    _summarizer_pipeline = None

def summarize_article(text: str, max_length=150, min_length=30) -> str:
    """
    Summarizes the given text using a pre-trained transformer model.
    Falls back to simple truncation if model is unavailable.
    """
    if not text:
        return ""
        
    try:
        # If text is too short, just return it
        if len(text.split()) < 50:
            return text
            
        if _summarizer_pipeline:
            # Chunking text if too long (simple handling)
            # HF pipelines handle truncation usually, but let's be safe
            input_text = text[:1024] 
            summary_list = _summarizer_pipeline(input_text, max_length=max_length, min_length=min_length, do_sample=False)
            if summary_list and len(summary_list) > 0:
                return summary_list[0]['summary_text']
        
        # Fallback: Return first 3 sentences
        sentences = text.split('.')
        return '.'.join(sentences[:3]) + '.'
        
    except Exception as e:
        print(f"Summarization error: {e}")
        return text[:500] + "..."
