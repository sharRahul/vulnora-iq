"""QLoRA fine-tuning for VulnoraIQ assistant model.

Usage:
    python model/train.py
    python model/train.py --base Qwen/Qwen2.5-1.5B-Instruct
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Fine-tune a small LLM for VulnoraIQ")
    p.add_argument("--base", default="Qwen/Qwen2.5-0.5B-Instruct",
                    help="HuggingFace base model")
    p.add_argument("--dataset", default=None,
                    help="Path to JSONL training file (default: auto-generated from OWASP docs)")
    p.add_argument("--output", default="./assistant-output",
                    help="Output directory for adapter + merged model")
    p.add_argument("--epochs", type=int, default=2, help="Training epochs (default: 2)")
    p.add_argument("--lr", type=float, default=2e-4, help="Peak learning rate (default: 2e-4)")
    p.add_argument("--batch-size", type=int, default=2, help="Per-device batch size (default: 2)")
    p.add_argument("--grad-accum", type=int, default=4, help="Gradient accumulation steps (default: 4)")
    p.add_argument("--max-seq-len", type=int, default=2048, help="Maximum sequence length (default: 2048)")
    p.add_argument("--lora-r", type=int, default=16, help="LoRA rank (default: 16)")
    p.add_argument("--lora-alpha", type=int, default=32, help="LoRA alpha (default: 32)")
    p.add_argument("--lora-dropout", type=float, default=0.0, help="LoRA dropout (default: 0.0)")
    p.add_argument("--hf-token", default=None, help="HuggingFace token for gated models")
    p.add_argument("--upload-to-hf", default=None,
                    help="Upload model to HF repo")
    return p.parse_args()


def load_dataset(path: Path) -> list[dict]:
    data = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            ex = json.loads(line)
            if "messages" in ex:
                data.append(ex)
    return data


def main() -> None:
    args = parse_args()
    script_dir = Path(__file__).parent
    dataset_path = Path(args.dataset) if args.dataset else script_dir / "train_dataset.jsonl"

    if not dataset_path.exists():
        print("Dataset not found. Generating from OWASP docs...")
        sys.path.insert(0, str(script_dir.resolve()))
        import prepare_dataset  # type: ignore[import-untyped]
        prepare_dataset.main()
        if not dataset_path.exists():
            print(f"Failed to generate dataset at {dataset_path}", file=sys.stderr)
            sys.exit(1)

    print(f"Loading dataset from {dataset_path}...")
    raw_data = load_dataset(dataset_path)
    print(f"Loaded {len(raw_data)} examples")

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, EarlyStoppingCallback
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training, PeftModel
    from datasets import Dataset
    from trl import SFTTrainer, SFTConfig

    chat_template = (
        "{% for message in messages %}"
        "{{ '<|im_start|>' + message['role'] + '\n' + message['content'] + '<|im_end|>' + '\n' }}"
        "{% endfor %}"
        "{% if add_generation_prompt %}{{ '<|im_start|>assistant\n' }}{% endif %}"
    )

    compute_dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=compute_dtype,
        bnb_4bit_use_double_quant=True,
    )

    print(f"Loading base model: {args.base} (compute: {compute_dtype})")
    tokenizer = AutoTokenizer.from_pretrained(args.base, token=args.hf_token, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.chat_template = chat_template

    model = AutoModelForCausalLM.from_pretrained(
        args.base,
        quantization_config=bnb_config,
        device_map="auto",
        torch_dtype=compute_dtype,
        token=args.hf_token,
        trust_remote_code=True,
        attn_implementation="sdpa",
    )
    model = prepare_model_for_kbit_training(model)

    model = get_peft_model(model, LoraConfig(
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    ))
    model.print_trainable_parameters()

    def apply_template(examples):
        return {"text": [tokenizer.apply_chat_template(msgs, tokenize=False) for msgs in examples["messages"]]}

    dataset = Dataset.from_list(raw_data)
    dataset = dataset.map(apply_template, batched=True)
    dataset = dataset.train_test_split(test_size=0.1, seed=42)
    train_data, eval_data = dataset["train"], dataset["test"]
    print(f"Train: {len(train_data)} | Eval: {len(eval_data)}")

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    training_args = SFTConfig(
        output_dir=str(output_dir),
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        warmup_ratio=0.1,
        num_train_epochs=args.epochs,
        learning_rate=args.lr,
        fp16=not torch.cuda.is_bf16_supported(),
        bf16=torch.cuda.is_bf16_supported(),
        logging_steps=5,
        eval_strategy="steps",
        eval_steps=0.1,
        save_strategy="steps",
        save_steps=0.2,
        save_total_limit=2,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        report_to="none",
        seed=42,
        ddp_find_unused_parameters=False,
        optim="adamw_8bit",
    )

    # Early stopping guards against the over-fitting seen previously (6 epochs drove
    # eval_loss to ~0.02 = memorisation). Note: with the current templated dataset the
    # eval split is drawn from the same distribution, so eval_loss understates
    # over-fitting; a held-out, human-written eval set is the real fix (Phase 2).
    trainer = SFTTrainer(
        model=model,
        processing_class=tokenizer,
        train_dataset=train_data,
        eval_dataset=eval_data,
        args=training_args,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=2)],
    )

    print("Starting training...")
    trainer.train()
    print("Training complete.")

    adapter_path = output_dir / "adapter"
    model.save_pretrained(str(adapter_path))
    tokenizer.save_pretrained(str(adapter_path))
    print(f"Adapter saved to: {adapter_path}")

    merged_path = output_dir / "merged"
    print("Merging LoRA weights...")
    del model
    torch.cuda.empty_cache()

    base = AutoModelForCausalLM.from_pretrained(
        args.base,
        torch_dtype=compute_dtype,
        device_map="auto",
        token=args.hf_token,
        trust_remote_code=True,
        attn_implementation="sdpa",
    )
    merged = PeftModel.from_pretrained(base, str(adapter_path))
    merged = merged.merge_and_unload()
    merged.save_pretrained(str(merged_path))
    tokenizer.save_pretrained(str(merged_path))
    print(f"Merged model saved to: {merged_path}")
    del merged, base
    torch.cuda.empty_cache()

    if args.upload_to_hf:
        try:
            from huggingface_hub import HfApi
            api = HfApi(token=args.hf_token)
            api.create_repo(args.upload_to_hf, exist_ok=True)
            api.upload_folder(folder_path=str(merged_path), repo_id=args.upload_to_hf, path_in_repo=".")
            print(f"Uploaded to: https://huggingface.co/{args.upload_to_hf}")
        except Exception as exc:
            print(f"Upload failed: {exc}", file=sys.stderr)

    print(f"\nDone! Merged model: {merged_path}")
    print(f"  Test inference with:")
    print(f"    python -c \"from transformers import AutoModelForCausalLM, AutoTokenizer; ...\"")


if __name__ == "__main__":
    main()
