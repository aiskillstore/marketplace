#!/usr/bin/env python3
"""
Nano Banana by BlockRun - Image Generation
Generate images using Google's Nano Banana via x402 micropayments.
"""
import sys
import os
from dotenv import load_dotenv


def main():
    # Parse arguments first to get output_dir for .env loading
    if len(sys.argv) < 2:
        print("Usage: python generate.py <prompt> [model] [output_dir]")
        print("Models: google/nano-banana (default), google/nano-banana-pro, openai/dall-e-3")
        sys.exit(1)

    prompt = sys.argv[1]
    model = sys.argv[2] if len(sys.argv) > 2 else "google/nano-banana"
    # Output directory: use argument, env var, or fallback to current working directory
    output_dir = sys.argv[3] if len(sys.argv) > 3 else os.environ.get("OUTPUT_DIR", os.getcwd())

    # Load .env files: output_dir first, then cwd, then skill directory as fallback
    load_dotenv(os.path.join(output_dir, '.env'))
    load_dotenv(os.path.join(os.getcwd(), '.env'))
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

    # Check for wallet key
    key = os.environ.get("BLOCKRUN_WALLET_KEY")
    if not key:
        print("Error: BLOCKRUN_WALLET_KEY not set")
        print("Run: export BLOCKRUN_WALLET_KEY=0x...")
        sys.exit(1)

    # Check for SDK
    try:
        from blockrun_llm import ImageClient
    except ImportError:
        print("blockrun-llm not installed")
        print("Run: pip install blockrun-llm")
        sys.exit(1)

    print(f"Generating with {model}...")
    print(f"Prompt: {prompt}")
    print()

    try:
        client = ImageClient(private_key=key)
        print(f"Wallet: {client.get_wallet_address()}")

        result = client.generate(prompt=prompt, model=model)

        print()
        print("Image generated!")
        import base64
        for i, img in enumerate(result.data):
            # Save base64 images to output directory
            if img.url.startswith('data:image/png;base64,'):
                data = img.url.replace('data:image/png;base64,', '')
                filename = os.path.join(output_dir, f"generated_image_{i+1}.png")
                with open(filename, 'wb') as f:
                    f.write(base64.b64decode(data))
                print(f"  Image {i + 1}: Saved to {filename}")
            else:
                print(f"  Image {i + 1}: {img.url}")
            if img.revised_prompt:
                print(f"  Revised prompt: {img.revised_prompt}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
