# Step 3 — GPU Assessment

**Goal**: Match detected hardware to known profiles and surface compatibility constraints.

Load and consult [gpu-profiles.md](../gpu-profiles.md).

For each GPU type detected in Step 1:
1. Look up the model in `gpu-profiles.md`
2. Report: VRAM per card, total cluster VRAM, supported dtypes, recommended attention backend
3. Surface compatibility warnings:

| GPU | Warning |
|-----|---------|
| T4 | Does not support bfloat16. Set `--dtype float16` in serving args. |
| V100 | Does not support bfloat16; limited flash attention. Use xformers backend. |

**CPU-only path:** Note CPU-only inference is available via KAITO + llama.cpp. Recommend `google/gemma-3-1b-it-qat-q8_0-gguf`.

Use the **Model Sizing Guide** in [model-sizing.md](../model-sizing.md) to calculate maximum model size for the cluster.
