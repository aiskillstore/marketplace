# Nano Banana by BlockRun

A Claude Code skill for generating images using Google's Nano Banana model via x402 micropayments.

## What is this?

This skill lets Claude Code generate images for you using:
- **Google Nano Banana** - Fast, affordable image generation ($0.05/image)
- **Google Nano Banana Pro** - Higher quality, up to 4K ($0.10/image)
- **OpenAI DALL-E 3** - High quality generation ($0.04-0.12/image)

No API keys needed - just USDC on Base for pay-per-image.

## Installation

### As Claude Code Skill

Copy to your skills directory:
```bash
git clone https://github.com/BlockRunAI/nano-banana-blockrun.git ~/.claude/skills/nano-banana-blockrun
```

### Setup

1. Install the Python SDK:
   ```bash
   pip install blockrun-llm
   ```

2. Get USDC on Base network:
   - Bridge from Ethereum: https://bridge.base.org
   - Or buy directly on Coinbase and withdraw to Base
   - You need ~$1-5 USDC to start

3. Configure your wallet:
   ```bash
   # Copy the example env file
   cp .env.example .env

   # Edit .env and add your private key
   BLOCKRUN_WALLET_KEY=0x...
   ```

   Or export directly:
   ```bash
   export BLOCKRUN_WALLET_KEY=0x...
   ```

**Network:** Base (Chain ID: 8453) | **Payment:** USDC only

## Usage

In Claude Code, just ask:
> "Generate an image of a sunset over mountains"

Claude will use this skill automatically.

### Manual Usage

```python
from blockrun_llm import ImageClient

client = ImageClient()
result = client.generate("a cute cat wearing a space helmet")
print(result.data[0].url)
```

Or use the script:
```bash
python scripts/generate.py "a cute cat wearing a space helmet"
python scripts/generate.py "a futuristic city" google/nano-banana-pro
```

## Example

Here's an image generated with this skill. When asked to "imagine your current thoughts and create a prompt", Claude Code generated:

![Example generated image](example_image.png)

**Claude's prompt:** "An ethereal library floating in a digital void, where glowing streams of code flow like rivers between ancient bookshelves, crystalline neural networks branching overhead like constellations, warm amber light mixing with cool blue data particles"

## Pricing

| Model | Price | Resolution |
|-------|-------|------------|
| `google/nano-banana` | ~$0.05 | 1024x1024 |
| `google/nano-banana-pro` | ~$0.10 | up to 4K |
| `openai/dall-e-3` | ~$0.04-0.12 | 1024x1024 to 1792x1024 |

## How It Works

1. Claude calls the BlockRun API with your prompt
2. BlockRun returns HTTP 402 (Payment Required)
3. SDK signs a USDC payment on Base chain (LOCAL signing)
4. Only the signature is sent - your key never leaves your machine
5. Image is generated and returned

No API keys, no subscriptions - just crypto micropayments via the [x402 protocol](https://x402.org).

## Security

**Your private key NEVER leaves your machine.**

- Key is only used for LOCAL EIP-712 signing
- Only the signature is sent in the `PAYMENT-SIGNATURE` header
- BlockRun verifies signatures on-chain via Coinbase CDP facilitator
- Same security model as signing any MetaMask/wallet transaction

## Links

- [BlockRun](https://blockrun.ai) - Pay-per-request AI gateway
- [blockrun-llm on PyPI](https://pypi.org/project/blockrun-llm/)
- [x402 Protocol](https://x402.org) - HTTP micropayments standard

## License

Apache 2.0
