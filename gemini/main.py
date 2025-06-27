import os
import re
import time
import json
from tqdm import tqdm
from pathlib import Path
from google.genai import types, Client

token = os.environ.get("GEMINI_API_KEY")

client = Client(api_key=token)

PROMPT = """There's an English word on the image. I want you to provide the following output:
* Title (English word from the image) - Its translation into Russian
* Definition of the English word from the image (If there's no definition of the word, write the definition yourself) - Translation of the definition into Russian."""

JSON_PROMPT = """There's an English word on the image. I want you to provide the output like this in JSON:
```json{
    "en": "word in english",
    "ru": "translated word into russian",
    "en_def": "definition of the word in english",
    "ru_def": "translated definition of the word into russian"
}
```
Note that, if there's no definition of the word on the image, write a definition yourself."""

img_dir_path = Path(r"D:\Programming\Projects\Word_Translation\june\images")

img_paths = [os.path.join(img_dir_path, x) for x in os.listdir(img_dir_path)]

def parse_json_block(text):
    """
    Extracts and parses a JSON code block from a given string.

    Args:
        text (str): String containing a JSON code block.

    Returns:
        dict: Parsed JSON as a Python dictionary.
    """
    # Use regex to find JSON inside ```json ... ```
    match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if not match:
        raise ValueError("No valid JSON block found.")
    
    json_str = match.group(1)
    return json.loads(json_str)

def translate_img(img_path: str | Path):
    print(f"[INFO] Opening: {img_path}...")
    try: 
        with open(img_path, 'rb') as f:
            image_bytes = f.read()
    except Exception as e:
        print(f"Failed opening img: {img_path}, skipping...")
        return {"response": f"failed to open image: {e}"}

    print("[INFO] Translating...")
    response = None
    try:
        response = client.models.generate_content(
        model='gemma-3-27b-it',
        contents=[
            types.Part.from_bytes(
            data=image_bytes,
            mime_type='image/jpeg',
            ),
            JSON_PROMPT
        ])
    except Exception as e:
        print(f"Failed request to the model: {e}")

    print("[INFO] Parsing JSON...")
    if response and hasattr(response, "text"):
        try:
            response_json = parse_json_block(response.text)
        except Exception as e:
            print(f"[ERROR] {e}, returning an unformatted json")    
            response_json = {
                'response': response.text
            }

    else:
        response_json = {
            "response": f"failed for img_path: {img_path}"
        }
        
    return response_json

if __name__=="__main__":
    translations = []
    
    # Get translation dictionaries
    for counter, img_path in enumerate(tqdm(img_paths, desc="Translating images")):
        if counter != 0 and counter % 30 == 0:
            print("[INFO] Rate limit pause — sleeping for 61 seconds...")
            time.sleep(61)

        translation_dict = translate_img(img_path)
        print(f"{translation_dict}\n\n")
        translations.append(translation_dict)
    
    # Save them
    with open('translates.json', 'w', encoding="utf-8") as file:
        json.dump(translations, file, indent=4, ensure_ascii=False)