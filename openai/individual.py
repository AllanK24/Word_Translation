import base64
import requests
import os
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("OPENAI_API_KEY")

# Set your OpenAI API key here
api_key = os.getenv(token)

# Function to encode the image in base64
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Function to process each image
def process_image(image_path, output_file):
    # Get the base64 string of the image
    base64_image = encode_image(image_path)

    # Prepare headers and payload for the API request
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": """You are a language translator. You will be shown an image with an English word and its definition. Your task is to provide the translation of the word and its definition into Russian. Usually there should be a definition of the word, but if there isn't, you can explain the word yourself.
                Please provide the translation in the following format: 
                Word (in English) - Translation of the word (in Russian)
                Definition (in English) - Translation of the definition (in Russian)""",
                "role": "user",
                "content": [
                    {"type": "text", "text": """There's an English word on the blackboard and definitions of this word (if there's no definition of the word on the blackboard, explain the word yourself), I want you to give me the following output: 
                    * Word (in English) - Translation (in Russian)
                    * Definition (in English) - Translation (in Russian)"""},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }
        ],
        "max_tokens": 300
    }

    # Make the API request
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    # Check if the response is successful
    if response.status_code == 200:
        result = response.json()
        # Extract the content from the response
        if 'choices' in result:
            content = result['choices'][0]['message']['content']
            # Format the result for output (optional: you can adjust formatting here)
            formatted_content = content.replace('\n\n', '\n').replace('- **', '').replace('**', '')
            # Save the result in the output file
            with open(output_file, 'a', encoding='utf-8') as f:
                f.write(f"Processed image: {image_path}\n")
                f.write(formatted_content + '\n\n')
            print(f"Processed and saved result for: {image_path}")
        else:
            print(f"No valid choices in response for image: {image_path}")
    else:
        print(f"Failed to process image {image_path} with status code: {response.status_code}")

# Main function to process all images in a folder sequentially
def process_images_in_folder(folder_path, output_txt_file):
    # Get all image paths in the folder
    image_paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.jpg')]

    # Check if output file exists, and clear it if necessary
    if os.path.exists(output_txt_file):
        os.remove(output_txt_file)

    # Process each image sequentially
    for image_path in image_paths:
        process_image(image_path, output_txt_file)

# Main script
if __name__ == "__main__":
    # Path to your images directory
    image_directory = r"D:\Programming\Projects\Word_Translation\june\images"
    output_txt_file = r'D:\Programming\Projects\Word_Translation\june\output.txt'

    # Start processing images sequentially
    process_images_in_folder(image_directory, output_txt_file)
    print(f"All images processed. Results saved in {output_txt_file}")
