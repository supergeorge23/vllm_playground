# Cloud Setup (Lambda Labs)

This guide is for running vLLM inference on a Lambda Labs GPU instance
while developing locally on macOS.

## Recommended Instance
- GPU: A100 (40GB or 80GB)
- OS: Ubuntu 22.04
- CUDA: 12.x

## One-Time Setup
```bash
sudo apt update
sudo apt install -y python3-venv git

python3 -m venv .venv
source .venv/bin/activate
pip install -U pip

pip install vllm

# Login to Hugging Face to access LLaMA-3 weights (requires approval)
pip install huggingface_hub
huggingface-cli login
```

## Model
- LLaMA-3 8B: `meta-llama/Meta-Llama-3-8B`

## Project Sync (example)
```bash
# Upload local project to the instance
rsync -av --exclude .venv ./ user@<lambda-host>:/path/to/project/

# Run inference on the instance
ssh user@<lambda-host> "cd /path/to/project && source .venv/bin/activate && python scripts/run_infer.py --config configs/run.yaml"

# Download results back to local
rsync -av user@<lambda-host>:/path/to/project/results/ ./results/
```

## Notes
- vLLM requires NVIDIA GPU + CUDA. It will not run on macOS locally.
- Keep results in `results/` (CSV/JSONL) so they can be pulled back to local.
