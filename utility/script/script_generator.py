import os
from openai import OpenAI
import json

if len(os.environ.get("GROQ_API_KEY")) > 30:
    from groq import Groq
    model = "mistral-saba-24b"
    client = Groq(
        api_key=os.environ.get("GROQ_API_KEY"),
        )
else:
    OPENAI_API_KEY = os.getenv('OPENAI_KEY')
    model = "gpt-4o"
    client = OpenAI(api_key=OPENAI_API_KEY)

def generate_script(topic):
    prompt = (
        """You are a seasoned content writer for a YouTube Shorts channel, specializing in facts videos. 
        Your facts shorts are concise, each lasting from 59-70 seconds (approximately 240 words). 
        They are incredibly engaging and original. When a user requests a specific type of facts short, you will create it.

        For instance, if the user asks for:
        Weird facts
        You would produce content like this:

        Weird facts you don't know:
        - Bananas are berries, but strawberries aren't.
        - A single cloud can weigh over a million pounds.
        - There's a species of jellyfish that is biologically immortal.
        - Honey never spoils; archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old and still edible.
        - The shortest war in history was between Britain and Zanzibar on August 27, 1896. Zanzibar surrendered after 38 minutes.
        - Octopuses have three hearts and blue blood.

        STRICT REQUIREMENTS:
        - Script MUST be 230-250 words (will produce 60-70 second audio)
        - Count the words and verify before responding
        - If under 230 words, add more facts
        - If over 250 words, remove less interesting facts
        
        Output ONLY this JSON format: {"script": "Your script here..."}
        """
    )
    
    for _ in range(3):  # Retry up to 3 times if word count fails
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": topic}
            ]
        )
        content = response.choices[0].message.content
        script = json.loads(content[content.find('{'):content.rfind('}')+1])["script"]
        
        word_count = len(script.split())
        if 230 <= word_count <= 250:
            return script
        print(f"Regenerating script (got {word_count} words, need 230-250)")
    
    raise ValueError(f"Failed to generate script with proper word count after 3 attempts")
