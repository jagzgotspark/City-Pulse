from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_city_summary(city_name: str, data: dict) -> str:
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{
                "role": "user",
                "content": f"""Generate a single vivid sentence (max 20 words) describing the current vibe of {city_name} right now:

Temperature: {data.get('temperature')}°C
Condition: {data.get('condition')}
AQI: {data.get('aqi')} (1=good, 5=very poor)
Pulse Score: {data.get('pulse_score')}/100

Write only the sentence. No preamble. No explanation. Make it vivid and human."""
            }],
            max_tokens=60
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"LLM error for {city_name}: {e}")
        return f"{city_name} data collected — summary unavailable."