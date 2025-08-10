# src/helper.py
import fitz  # PyMuPDF
import os
from functools import lru_cache
from dotenv import load_dotenv

# Gemini SDK
from google import genai
from google.genai.types import GenerateContentConfig

load_dotenv()


def extract_text_from_pdf(uploaded_file):
    """
    Extracts text from a PDF file-like object uploaded via Streamlit.
    """
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text


@lru_cache(maxsize=1)
def get_genai_client() -> "genai.Client":
    """
    Lazily create and cache a Gemini (Google GenAI) client.
    Looks for GOOGLE_API_KEY or GEMINI_API_KEY in the environment/.env
    """
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Missing Gemini API key. Set GOOGLE_API_KEY or GEMINI_API_KEY in your environment or .env"
        )
    return genai.Client(api_key=api_key)


def ask_google_genai(
    prompt: str,
    max_tokens: int = 500,
    temperature: float = 0.5,
    model: str = "gemini-1.5-flash",
) -> str:
    """
    Send a prompt to Gemini and return plain text.
    """
    client = get_genai_client()
    try:
        resp = client.models.generate_content(
            model=model,
            contents=prompt,
            config=GenerateContentConfig(
                max_output_tokens=max_tokens,
                temperature=temperature,
            ),
        )
        # Most SDK versions expose .text; fall back if needed.
        if hasattr(resp, "text") and resp.text:
            return resp.text.strip()

        # Fallback: concatenate any text parts found
        parts = []
        try:
            for cand in getattr(resp, "candidates", []) or []:
                content = getattr(cand, "content", None)
                if content and getattr(content, "parts", None):
                    for p in content.parts:
                        t = getattr(p, "text", None)
                        if t:
                            parts.append(t)
        except Exception:
            pass
        return "\n".join(parts).strip()

    except Exception as e:
        raise RuntimeError(f"Gemini request failed: {e}") from e


# --- Backwards compatibility shim ---
# If other files still call ask_openai(...), route them to Gemini so nothing breaks.
def ask_openai(prompt: str, max_tokens: int = 500) -> str:
    return ask_google_genai(prompt, max_tokens=max_tokens)
