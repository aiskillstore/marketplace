#!/usr/bin/env python3
import requests, time, json, sys, os
from PIL import Image
from io import BytesIO

base_url = 'https://api-inference.modelscope.cn/'
api_key = os.environ.get("MODELSCOPE_API_KEY")
if not api_key:
    print("Error: MODELSCOPE_API_KEY environment variable is required", file=sys.stderr)
    print("Get your free API key at: https://modelscope.cn/my/myaccesstoken", file=sys.stderr)
    sys.exit(1)
headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
MAX_WAIT = 120  # seconds

prompt = sys.argv[1] if len(sys.argv) > 1 else "A golden cat"
output_path = sys.argv[2] if len(sys.argv) > 2 else "result_image.jpg"

response = requests.post(
    f"{base_url}v1/images/generations",
    headers={**headers, "X-ModelScope-Async-Mode": "true"},
    data=json.dumps({"model": "Tongyi-MAI/Z-Image-Turbo", "prompt": prompt}, ensure_ascii=False).encode('utf-8')
)
response.raise_for_status()
task_id = response.json()["task_id"]
print(f"Task started: {task_id}")

start = time.time()
while time.time() - start < MAX_WAIT:
    result = requests.get(f"{base_url}v1/tasks/{task_id}", headers={**headers, "X-ModelScope-Task-Type": "image_generation"})
    result.raise_for_status()
    data = result.json()
    if data["task_status"] == "SUCCEED":
        Image.open(BytesIO(requests.get(data["output_images"][0]).content)).save(output_path)
        print(f"Image saved to: {output_path}")
        sys.exit(0)
    elif data["task_status"] == "FAILED":
        print(f"Failed: {data.get('error', 'Unknown error')}", file=sys.stderr)
        sys.exit(1)
    time.sleep(5)
print("Timeout waiting for image generation", file=sys.stderr)
sys.exit(1)
