from groq import Groq
from config.settings import GROQ_API_KEY

def translate_to_hindi(text):
    """
    Translates English text to Hindi using Groq API.
    """
    if not GROQ_API_KEY:
        return text  # Return original text if no API key
    
    try:
        client = Groq(api_key=GROQ_API_KEY)
        
        prompt = f"Translate the following English text to Hindi. Only provide the Hindi translation, nothing else:\n\n{text}"
        
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.3-70b-versatile",
        )
        
        return chat_completion.choices[0].message.content
    
    except Exception as e:
        print(f"Translation error: {e}")
        return text  # Return original text on error
