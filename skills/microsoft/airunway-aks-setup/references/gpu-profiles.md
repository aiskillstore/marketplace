# GPU Compatibility Reference

This reference is used by the `airunway-aks-setup` skill during **Step 3 — GPU Assessment** to match detected GPU hardware to known compatibility profiles and surface constraints before model deployment.

## GPU Profiles

| GPU Model | VRAM (GB) | bfloat16 | float16 | Attention Backends | Compute Capability | Notes |
|-----------|-----------|----------|---------|-------------------|-------------------|-------|
| T4 | 16 | No | Yes | XFORMERS | 7.5 | No bfloat16 — must use float16 or float32. |
| V100 (16 GB) | 16 | No | Yes | XFORMERS | 7.0 | Limited flash attention. Prefer xformers. |
| V100 (32 GB) | 32 | No | Yes | XFORMERS | 7.0 | Same dtype constraints as 16 GB variant. |
| A10 | 24 | Yes | Yes | FLASH_ATTN, XFORMERS | 8.6 | Single-slot Ampere GPU. |
| A10G | 24 | Yes | Yes | FLASH_ATTN, XFORMERS | 8.6 | Good general-purpose GPU. Common in AWS. |
| L4 | 24 | Yes | Yes | FLASH_ATTN, XFORMERS | 8.9 | Inference-optimized. Common in GCP and Azure. |
| L40S | 48 | Yes | Yes | FLASH_ATTN, TRITON_ATTN, XFORMERS | 8.9 | Ada Lovelace. Growing availability on Azure. |
| A100 (40 GB) | 40 | Yes | Yes | FLASH_ATTN, TRITON_ATTN, XFORMERS | 8.0 | High-performance training and inference. |
| A100 (80 GB) | 80 | Yes | Yes | FLASH_ATTN, TRITON_ATTN, XFORMERS | 8.0 | Recommended for large models (70B+). |
| H100 | 80 | Yes | Yes | FLASH_ATTN, TRITON_ATTN, XFORMERS | 9.0 | Highest single-GPU performance. |
| H200 (SXM) | 141 | Yes | Yes | FLASH_ATTN, TRITON_ATTN, XFORMERS | 9.0 | Maximum memory (HBM3e). |
| H20 | 96 | Yes | Yes | FLASH_ATTN, TRITON_ATTN, XFORMERS | 9.0 | China-market H100 derivative. 96 GB HBM3. |

### Attention Backends

| Backend | Description | Min Compute Capability |
|---------|-------------|----------------------|
| FLASH_ATTN | FlashAttention-2 — fastest, lowest memory | 8.0 (Ampere+) |
| TRITON_ATTN | Triton-based attention — good performance | 8.0 (Ampere+) |
| XFORMERS | Memory-efficient attention — works on older GPUs | 7.0 (Volta+) |

## Compatibility Warnings

Surface these warnings when the following GPUs are detected:

### T4
> **Warning:** T4 GPUs do not support bfloat16. You must configure `--dtype float16` in serving arguments. Failure to do so causes errors or silent dtype casting.

### V100
> **Warning:** V100 GPUs do not support bfloat16 and have limited flash attention support. Use xformers backend and `--dtype float16`.

## Model Sizing & Recommendations

For VRAM sizing estimates and starter model recommendations, see [model-sizing.md](model-sizing.md).
