import base64
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

def generate(prompt):
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    model = "gemini-2.5-rpo"

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=prompt),
            ],
        ),
    ]

    generate_content_config = types.GenerateContentConfig(
        temperature = 0.2,
        thinking_config = types.ThinkingConfig(
            thinking_budget=-1,
        ),
        image_config=types.ImageConfig(
            image_size="1K",
        ),
    )

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        print(chunk.text, end="")

if __name__ == "__main__":
    prompt = """
    Try to find the contact information of this person from these URLs:
    https://robertsonscholars.org/profiles/harjyot-singh-sahni/
    https://ousf.duke.edu/profile/harjyot-singh-sahni/
    https://www.linkedin.com/in/harjyotsahni
    """
    generate(prompt)