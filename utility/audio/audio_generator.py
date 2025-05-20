import edge_tts

async def generate_audio(text, outputFilename):
    communicate = edge_tts.Communicate(
        text,
        voice="en-AU-WilliamNeural",
        rate="+15%"  # Slower speech (experiment with -10% to +20%)
    )
    await communicate.save(outputFilename)











