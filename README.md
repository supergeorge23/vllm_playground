# RAG Prefill–Decode Asymmetry

This project studies the **prefill–decode asymmetry** in Retrieval-Augmented Generation (RAG) inference and explores system-level designs to exploit this asymmetry for improved latency and throughput.

The focus is **LLM inference systems**, not model training.

---

## Requirements

### Model
- LLaMA-3 8B (decoder-only)
- FP16 / BF16 inference

### Runtime
- vLLM (explicit prefill / decode execution)
- No high-level inference DSLs (e.g., SGLang) in early stages

### Hardware
- Single NVIDIA GPU (A100-class)
- CUDA 12.x
- Ubuntu 22.04

### Workload Characteristics
- Long RAG context (2k–16k tokens)
- Short user query
- Short decode output (≤ 150 tokens)

---

## Project Goals

1. Quantify prefill vs decode latency under RAG-style workloads
2. Measure the impact of context length on TTFT and throughput
3. Expose system-level causes of prefill dominance
4. Establish a baseline for future prefill–decode decoupling designs

---

## Planned Workflow

### Phase 1 — Baseline Inference
- Run LLaMA-3 8B with vLLM
- Generate synthetic RAG prompts with varying context lengths
- Measure:
  - Time to First Token (TTFT)
  - Decode throughput (tokens/sec)
  - GPU memory usage

### Phase 2 — Prefill / Decode Profiling
- Separate and instrument prefill and decode execution
- Analyze KV cache allocation and attention behavior

### Phase 3 — System Exploration
- Prefill–decode decoupling
- Context KV cache reuse
- Latency–memory trade-offs

---

## Development Workflow

- Code is written locally (macOS)
- Experiments are executed on cloud GPUs (Lambda Labs)
- Results are logged as JSONL for analysis

## Project Structure

```
Playground/
├── configs/              # Configuration files (YAML)
│   └── baseline.yaml     # Baseline inference config
├── scripts/              # Python scripts
│   ├── workflow.py       # Main workflow orchestrator
│   ├── generate_rag_prompts.py  # Generate synthetic RAG prompts
│   └── run_baseline.py   # Baseline inference benchmark
├── data/                 # Input data (prompts, etc.)
├── results/              # Output results (JSONL/CSV)
├── requirements.txt      # Python dependencies
└── USAGE.md             # Detailed usage guide
```

## Quick Start

### Local Development (macOS)

```bash
# Generate test prompts locally
python scripts/generate_rag_prompts.py --num-samples 5
```

### Cloud Execution (Lambda Labs)

```bash
# 1. Sync project to cloud
rsync -av --exclude .venv ./ user@<host>:/path/to/project/

# 2. SSH and run workflow
ssh user@<host>
cd /path/to/project
source .venv/bin/activate
python scripts/workflow.py --phase 1

# 3. Download results
rsync -av user@<host>:/path/to/project/results/ ./results/
```

See `USAGE.md` for detailed instructions.

---

## Testing

Run unit tests to verify functionality:

```bash
# Test logger system
python scripts/utils/test_logger.py

# Test prompt generation
python scripts/test_generate_prompts.py
```

See `USAGE.md` for detailed testing instructions.

---

## Status

- [x] Project structure and workflow framework
- [x] Baseline benchmark implementation (Phase 1)
- [x] Unified logger system with unit tests
- [ ] Cloud GPU environment ready
- [ ] Prefill–decode profiling (Phase 2)
- [ ] System optimization experiments (Phase 3)
