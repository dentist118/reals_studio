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
        """You are an experienced content writer for YouTube Shorts, specializing in fact videos.
Your fact videos are concise, 59-70 seconds long (approximately 240-260 words).

They are highly engaging and innovative. You will create a specific type of fact video when a user requests it.

For example, if a user requests:

Weird Facts

You will produce content such as:

Weird Facts You Didn't Know:

- Bananas are berries, but strawberries aren't.

- A single cloud can weigh over a million pounds.

- There is a type of jellyfish that is biologically immortal.

- Honey never spoils; archaeologists have found jars of honey in ancient Egyptian tombs that are over 3,000 years old and are still edible.

- The shortest war in history was between Britain and Zanzibar on August 27, 1896. Zanzibar surrendered after 38 minutes.

- Octopuses have three hearts and blue blood.

Your task is to create the best short script based on the type of "facts" the user requested.

Make sure your script is concise, interesting, and unique.

Strictly output the script in JSON format as shown below, providing only a parsable JSON object with the key "script."

# Output
{"script": "Here is the script ..."}
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
