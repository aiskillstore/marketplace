---
name: nano-banana-blockrun
description: "Nano Banana by BlockRun - Generate images using Google's Nano Banana via x402 micropayments. Use when the user asks to generate, create, draw, or make images. Pay-per-request via USDC on Base, no API keys needed."
allowed-tools: Read, Bash(python:*), Bash(python3:*), Bash(pip:*), Bash(pip3:*)
---

# Nano Banana by BlockRun

Generate images using Google's Nano Banana model via BlockRun's x402 API.
Pay-per-request with USDC on Base - no API keys needed.

## Setup (one-time)

1. Install the SDK:
   ```bash
   pip install blockrun-llm
   ```

2. Get USDC on Base network:
   - Bridge from Ethereum: https://bridge.base.org
   - Or buy directly on Coinbase and withdraw to Base
   - You need ~$1-5 USDC to start generating images

3. Set your wallet private key:
   ```bash
   # Copy .env.example to .env and add your key
   cp .env.example .env

   # Or export directly
   export BLOCKRUN_WALLET_KEY=0x...
   ```

**Network:** Base (Chain ID: 8453)
**Payment:** USDC only

## Generate an Image

```python
from blockrun_llm import ImageClient

client = ImageClient()
result = client.generate("a cute cat wearing a space helmet")
print(result.data[0].url)
```

Or use the script:
```bash
python scripts/generate.py "a cute cat wearing a space helmet"

# Save to a specific directory
python scripts/generate.py "a cute cat" "google/nano-banana" "/path/to/save"

# Or use OUTPUT_DIR environment variable
OUTPUT_DIR=/path/to/save python scripts/generate.py "a cute cat"
```

## Available Models

| Model | Price | Resolution |
|-------|-------|------------|
| `google/nano-banana` | ~$0.05 | 1024x1024 |
| `google/nano-banana-pro` | ~$0.10 | up to 4K |
| `openai/dall-e-3` | ~$0.04-0.12 | 1024x1024 to 1792x1024 |

## How It Works

1. Your request goes to BlockRun API (https://blockrun.ai)
2. BlockRun returns HTTP 402 Payment Required
3. SDK signs USDC payment locally (key never leaves your machine)
4. Only the signature is sent to server
5. Image is generated and returned

No API keys, no subscriptions - just crypto micropayments.

## Security

**Your private key NEVER leaves your machine.**

The SDK uses EIP-712 typed data signing locally. Only the signature is transmitted.
Same security as signing any MetaMask transaction.

## Links

- [BlockRun](https://blockrun.ai)
- [x402 Protocol](https://x402.org)
- [PyPI Package](https://pypi.org/project/blockrun-llm/)
