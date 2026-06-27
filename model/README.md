# VulnoraIQ assistant model — training pipeline

Train a small instruction-tuned model for the VulnoraIQ assistant.

## Quick start

```bash
# 1. Install training deps
pip install -r vulnoraiq/model/requirements-train.txt

# 2. Generate dataset from OWASP docs
python vulnoraiq/model/prepare_dataset.py

# 3. Train (QLoRA, ~20-40 min on 16 GB GPU)
python vulnoraiq/model/train.py
```

The script creates `./vulnoraiq-assistant/` with:
- `adapter/` — LoRA adapter weights (~10 MB)
- `merged/` — Full merged model in HF format
- `vulnoraiq-assistant-q4_k_m.gguf` — GGUF model ready for VulnoraIQ

Test it with:

```bash
VULNORAIQ_ASSISTANT_MODEL_PATH=./assistant-output/vulnoraiq-assistant-Q4_K_M.gguf \
    python -c "from webui.assistant_llm import LocalAssistantModel; \
    m = LocalAssistantModel.instance(); \
    print(m.generate([{'role':'user','content':'What is prompt injection?'}], temperature=0.2, max_tokens=256))"
```

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `--base` | Qwen/Qwen2.5-0.5B-Instruct | Base model (try 1.5B or 3B for better quality) |
| `--dataset` | auto (from OWASP docs) | Custom JSONL dataset path |
| `--epochs` | 2 | Training epochs (early stopping on eval_loss also enabled) |
| `--lr` | 2e-4 | Peak learning rate |
| `--batch-size` | 2 | Per-device batch size |
| `--grad-accum` | 4 | Gradient accumulation steps |
| `--max-seq-len` | 2048 | Max sequence length |
| `--lora-r` | 16 | LoRA rank |
| `--gguf-quant` | q4_k_m | GGUF quantization type |
| `--upload-to-hf` | — | Upload adapter to HuggingFace repo |

## Dataset format

JSONL with `messages` key (OpenAI chat format):

```jsonl
{"messages": [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]}
```

Run `prepare_dataset.py` to generate from OWASP docs. Add your own examples by appending to the output JSONL.

## Model recommendations

| Model | Params | VRAM | Quality |
|-------|--------|------|---------|
| Qwen2.5-0.5B-Instruct | 0.5B | ~4 GB | Good for basic guidance |
| Qwen2.5-1.5B-Instruct | 1.5B | ~6 GB | Better explanations |
| Qwen2.5-3B-Instruct | 3B | ~8 GB | Best quality on 16 GB GPU |
| Llama-3.2-1B-Instruct | 1B | ~5 GB | Good alternative |
| Gemma-2-2B | 2B | ~7 GB | Good alternative |

## Hosting for VulnoraIQ distribution

After training, upload the GGUF to HuggingFace:

```bash
python vulnoraiq/model/train.py --upload-to-hf youruser/vulnoraiq-assistant
```

Users set these env vars to pull your model:

```
VULNORAIQ_ASSISTANT_MODEL_REPO=youruser/vulnoraiq-assistant
VULNORAIQ_ASSISTANT_MODEL_FILE=vulnoraiq-assistant-q4_k_m.gguf
```

The first-run autodownload will fetch it automatically.

## Manual GGUF conversion

If the built-in export fails:

```bash
git clone https://github.com/ggerganov/llama.cpp
python llama.cpp/convert_hf_to_gguf.py vulnoraiq-assistant/merged \
    --outtype q4_k_m -o vulnoraiq-assistant-q4_k_m.gguf
```
