import google.generativeai as genai
from django.conf import settings

genai.configure(api_key=settings.GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")

def generate_ai_reply(prompt):
    response = model.generate_content(prompt)
    return response.text
