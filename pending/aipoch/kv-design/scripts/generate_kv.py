import os
import sys
from zhipuai import ZhipuAI
import requests

def generate_kv(prompt):
    api_key = os.getenv("ZHIPUAI_API_KEY")
    if not api_key:
        print("Error: ZHIPUAI_API_KEY environment variable is not set.")
        print("Please set it via: $env:ZHIPUAI_API_KEY='your_key' (PowerShell) or set ZHIPUAI_API_KEY=your_key (CMD)")
        return

    client = ZhipuAI(api_key=api_key)

    try:
        print(f"Generating KV design for prompt: {prompt[:50]}...")
        # Using cogview-3-plus or cogview-3 if available
        response = client.images.generations(
            model="cogview-3", 
            prompt=prompt,
        )
        
        if response.data:
            image_url = response.data[0].url
            print(f"KV generated successfully!")
            print(f"Image URL: {image_url}")
            
            # Download
            img_data = requests.get(image_url).content
            filename = "kv_design_generated.png"
            # If file exists, append number
            counter = 1
            while os.path.exists(filename):
                filename = f"kv_design_generated_{counter}.png"
                counter += 1
                
            with open(filename, 'wb') as handler:
                handler.write(img_data)
            print(f"Image saved to: {os.path.abspath(filename)}")
        else:
            print("Failed to generate image (No data returned).")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_kv.py <prompt>")
        sys.exit(1)
    
    prompt = sys.argv[1]
    generate_kv(prompt)
