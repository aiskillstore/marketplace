import os
import sys
from zhipuai import ZhipuAI

def generate_image(prompt):
    api_key = os.getenv("ZHIPUAI_API_KEY")
    if not api_key:
        print("Error: ZHIPUAI_API_KEY environment variable is not set.")
        print("Please set it via: $env:ZHIPUAI_API_KEY='your_key' (PowerShell) or set ZHIPUAI_API_KEY=your_key (CMD)")
        return

    client = ZhipuAI(api_key=api_key)

    try:
        print(f"Generating image for prompt: {prompt[:50]}...")
        response = client.images.generations(
            model="cogview-3", # Using CogView-3
            prompt=prompt,
        )
        
        if response.data:
            image_url = response.data[0].url
            print(f"Image generated successfully!")
            print(f"Image URL: {image_url}")
            # In a real scenario, we might download it. For now, returning URL is good.
            # Let's try to download it to current folder
            import requests
            img_data = requests.get(image_url).content
            filename = "poster_generated.png"
            with open(filename, 'wb') as handler:
                handler.write(img_data)
            print(f"Image saved to: {os.path.abspath(filename)}")
        else:
            print("Failed to generate image (No data returned).")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_image.py <prompt>")
        sys.exit(1)
    
    prompt = sys.argv[1]
    generate_image(prompt)
