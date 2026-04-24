# Model Sizing & Starter Recommendations

## VRAM Sizing Guide

Estimate how much VRAM a model requires. Values are **weights only** — add 20–30% overhead for KV cache and activations during inference.

| Parameters | float16 / bfloat16 | int8 | int4 / GGUF Q4 |
|-----------|-------------------|------|----------------|
| 1B | ~2 GB | ~1 GB | ~0.5 GB |
| 3B | ~6 GB | ~3 GB | ~1.5 GB |
| 7–8B | ~14–16 GB | ~7–8 GB | ~3.5–4 GB |
| 13B | ~26 GB | ~13 GB | ~6.5 GB |
| 34B | ~68 GB | ~34 GB | ~17 GB |
| 70B | ~140 GB | ~70 GB | ~35 GB |

**Example:** 4× A100 80 GB = 320 GB total. Llama-3.1-70B at bfloat16 ≈ 168 GB with overhead — fits across 4 GPUs with tensor parallelism.

## Starter Model Recommendations

| Cluster Capacity | Model | Provider | Notes |
|-----------------|-------|----------|-------|
| CPU-only | `google/gemma-3-1b-it-qat-q8_0-gguf` | KAITO (llama.cpp) | GGUF Q8; runs on CPU |
| 1× T4 (16 GB) | `microsoft/Phi-3-mini-4k-instruct` | KAITO (vLLM) | ~8 GB float16; fits with headroom |
| 1× A10G/L4 (24 GB) | `meta-llama/Llama-3.1-8B-Instruct` | KAITO (vLLM) | ~16 GB bfloat16; gated — needs HF token |
| 1× A100 40 GB | `microsoft/Phi-3-medium-128k-instruct` | KAITO (vLLM) | ~28 GB float16; non-gated; MIT license |
| 1× A100 80 GB / H100 | `meta-llama/Llama-3.1-8B-Instruct` | KAITO (vLLM) | Oversized; upgrade to 70B if more GPUs available |
| 4× A100 80 GB | `meta-llama/Llama-3.1-70B-Instruct` | KAITO (vLLM, TP) | ~168 GB; tensor parallelism; gated |

### Gated Models

These models are **gated on HuggingFace** and require an access token:
- `meta-llama/Llama-3.1-8B-Instruct`
- `meta-llama/Llama-3.1-70B-Instruct`

**Non-gated alternatives** (no token required):
- `microsoft/Phi-3-mini-4k-instruct` (MIT license)
- `microsoft/Phi-3-medium-128k-instruct` (MIT license)
- `google/gemma-3-1b-it-qat-q8_0-gguf` (Gemma license)
