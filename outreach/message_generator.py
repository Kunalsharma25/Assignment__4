import os
import google.generativeai as genai
from groq import Groq
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()

def generate_outreach_messages(creators: List[Dict], brand: Dict) -> List[Dict]:
    """Generates personalized email pitches using Groq (primary) or Gemini (fallback)."""
    groq_key = os.getenv("GROQ_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    # Initialize clients
    groq_client = None
    if groq_key and "YOUR_GROQ_API_KEY" not in groq_key:
        try:
            groq_client = Groq(api_key=groq_key)
        except Exception as e:
            print(f"[Outreach] Error initializing Groq: {e}")

    if gemini_key and "YOUR_GEMINI_API_KEY" not in gemini_key:
        genai.configure(api_key=gemini_key)
        try:
            gemini_model = genai.GenerativeModel("gemini-flash-lite-latest")
            gemini_model.generate_content("test")
        except Exception:
            gemini_model = genai.GenerativeModel("gemini-pro-latest")
    else:
        gemini_model = None

    if not groq_client and not gemini_model:
        print("[Outreach] Warning: No valid LLM API keys found (Groq or Gemini). Skipping message generation.")
        return creators

    print(f"[Outreach] Generating messages for {len(creators)} creators...")
    
    import time
    from outreach.email_verifier import verify_email
    generated_count = 0
    
    for creator in creators:
        email_addr = creator.get("contact_email")
        
        # Only verify if email exists, but don't skip the whole creator if it doesn't
        if email_addr:
            is_valid, reason = verify_email(email_addr)
            if not is_valid:
                email_addr = None # Reset if invalid, but still generate DM
            
        # Robust Null Check: Only generate if we have a real email string
        if not email_addr or str(email_addr).lower() in ["none", "null", "nan", ""]:
            continue
        
        # Rate limiting sleep
        if generated_count > 0:
            sleep_time = 2 if groq_client else 12
            print(f"[Outreach] Rate limiting: Sleeping for {sleep_time}s before generating for {creator.get('channel_title')}...")
            time.sleep(sleep_time)
        
        prompt = f"""
        You are a brand partnership manager at {brand.get('name')}.
        Task: Write a personalized email pitch to a content creator.
        
        Creator: {creator.get('channel_title')}
        Themes: {', '.join(creator.get('content_themes', []))}
        Strategy: {creator.get('collaboration_strategy')}
        Brand Offering: {brand.get('offering')}
        
        Requirements:
        - Length: 60-90 words.
        - Reference their specific content themes.
        - Professional but warm tone.
        - Write only the email body.
        """
        
        content = None
        # Try Groq first
        if groq_client:
            try:
                response = groq_client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.1-8b-instant",
                )
                content = response.choices[0].message.content.strip()
                print(f"[Outreach] Generated using Groq for {creator.get('channel_title')}")
            except Exception as e:
                print(f"[Outreach] Groq failed for {creator.get('channel_title')}: {str(e)}")

        # Fallback to Gemini
        if not content and gemini_model:
            try:
                response = gemini_model.generate_content(prompt)
                content = response.text.strip()
                print(f"[Outreach] Generated using Gemini for {creator.get('channel_title')}")
            except Exception as e:
                print(f"[Outreach] Gemini error: {str(e)[:50]}...")

        if content:
            creator["outreach_email"] = content
            generated_count += 1
        else:
            creator["outreach_email"] = None
            
    return creators
