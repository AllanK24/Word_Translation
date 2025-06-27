import openai
import base64
import json
import os
import time
from dotenv import load_dotenv

load_dotenv()

# Set your OpenAI API key
openai.api = os.getenv("OPENAI_API_KEY")

# Function to encode images in base64
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Function to create JSONL file for batch processing
def create_jsonl(image_paths, output_file):
    with open(output_file, 'w') as outfile:
        for idx, image_path in enumerate(image_paths):
            base64_image = encode_image(image_path)
            request = {
                "custom_id": f"Image-{idx}",
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": "gpt-4o",
                    "messages": [
                        {"role": "user", "content": [
                            {"type": "text", "text": """There's an English word on the blackboard and definitions of this word. I want you to provide the following output:
                            * Title (English word from the image) - Its translation into Russian
                            * Definition of the English word from the image - Translation of the definition into Russian"""},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                        ]}
                    ],
                    "max_tokens": 300
                }
            }
            outfile.write(json.dumps(request) + '\n')

# Function to create a batch job
def create_batch_job(jsonl_file):
    # Upload the JSONL file
    batch_input_file = openai.files.create(
        file=open(jsonl_file, 'rb'),
        purpose='batch'
    )

    # Create the batch job with a 2-hour completion window
    batch = openai.batches.create(
        input_file_id=batch_input_file.id,
        endpoint="/v1/chat/completions",
        completion_window='24h',  # Adjust as needed
        metadata={
            'description': 'Batch processing of images for word translation'
        }
    )

    print(f"Batch job created with ID: {batch.id}")
    return batch.id

# Function to monitor the batch job and download results
def monitor_batch_and_save_results(batch_id, output_txt_file):
    while True:
        batch = openai.batches.retrieve(batch_id)
        status = batch.status
        print(f"Batch status: {status}")

        if status == 'completed':
            # Download the results
            results_file = openai.files.content(batch.output_file_id)
            
            print(f"Results downloaded to: {results_file}")

            # Process the results and save to a text file
            with open(results_file, 'r') as infile, open(output_txt_file, 'w') as outfile:
                for line in infile:
                    result = json.loads(line)
                    if 'choices' in result:
                        # Extract and format the desired output
                        content = result['choices'][0]['message']['content']
                        formatted_content = content.replace('\n\n', '\n').replace('- **', '').replace('**', '')
                        outfile.write(formatted_content + '\n\n')
            print(f"Formatted results saved to: {output_txt_file}")
            break
        elif status == 'failed':
            print("Batch processing failed.")
            break
        else:
            print("Waiting for batch to complete...")
            time.sleep(60)  # Check status every 60 seconds

# Main script
if __name__ == "__main__":
    # Path to your images directory
    image_directory = r"D:\Programming\Projects\Word_Translation\test"
    jsonl_file = 'batch_requests.jsonl'
    output_txt_file = 'batch_results.txt'

    # Step 1: Collect all image paths
    image_paths = [os.path.join(image_directory, f) for f in os.listdir(image_directory) if f.endswith('.jpg')]

    # Step 2: Create JSONL file for batch processing
    create_jsonl(image_paths, jsonl_file)
    print(f"JSONL file created: {jsonl_file}")

    # Step 3: Create a batch job
    batch_id = create_batch_job(jsonl_file)

    # Step 4: Monitor batch job and save results
    monitor_batch_and_save_results(batch_id, output_txt_file)
