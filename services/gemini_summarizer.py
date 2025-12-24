# GEMINI CODE (COMMENTED OUT - Using Groq instead)
# from google import genai
# from config.settings import GEMINI_API_KEYS
# 
# def summarize_text_gemini(text):
#     """
#     Summarizes the given text using Google Gemini (New SDK).
#     Iterates through available API keys if one fails (e.g., due to quota).
#     """
#     if not GEMINI_API_KEYS:
#         return "Error: No GEMINI_API_KEY found in environment variables."
# 
#     last_error = None
# 
#     for api_key in GEMINI_API_KEYS:
#         try:
#             # Initialize the client from the new SDK with current key
#             client = genai.Client(api_key=api_key)
#             
#             prompt = f"Summarize the following news article in 2-3 concise sentences. Focus on the main facts:\n\n{text}"
#             
#             # Use the models.generate_content method
#             response = client.models.generate_content(
#                 model='gemini-2.0-flash-lite', 
#                 contents=prompt
#             )
#             
#             # If successful, return immediately
#             return response.text
# 
#         except Exception as e:
#             # If error, save it and try the next key
#             last_error = e
#             print(f"Key failed: {str(e)[:100]}... Trying next key.")
#             continue
#     
#     # If all keys failed
#     return f"Error generating summary (All keys failed): {str(last_error)}"


# NEW GROQ IMPLEMENTATION
from groq import Groq
from config.settings import GROQ_API_KEY

def summarize_text(text):
    """
    Summarizes the given text using Groq API.
    """
    if not GROQ_API_KEY:
        return "Error: No GROQ_API_KEY found in environment variables."

    try:
        # Initialize the Groq client
        client = Groq(api_key=GROQ_API_KEY)
        
        prompt = f"Summarize the following news article in 2-3 concise sentences. Focus on the main facts:\n\n{text}"
        
        # Create chat completion
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.3-70b-versatile",  # Using Llama 3.3 70B model
        )
        
        # Return the response
        return chat_completion.choices[0].message.content

    except Exception as e:
        return f"Error generating summary with Groq: {str(e)}"
