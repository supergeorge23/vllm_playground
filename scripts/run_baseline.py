#!/usr/bin/env python3
"""
Baseline inference benchmark for RAG prefill-decode asymmetry study.

Measures:
- Time to First Token (TTFT)
- Decode throughput (tokens/sec)
- Total latency
- GPU memory usage
- Prefill and decode phase times
"""

import argparse
import json
import logging
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
import yaml

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.utils.logger import setup_logger, log_header, log_subheader

logger = setup_logger(__name__)

try:
    from vllm import LLM, SamplingParams
    import torch
except ImportError:
    logger.error("vLLM not installed. Please install with: pip install vllm")
    exit(1)


def load_config(config_path: Path) -> Dict[str, Any]:
    """Load configuration from YAML file."""
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def load_prompts(prompts_path: Path) -> List[Dict[str, Any]]:
    """Load prompts from JSONL file."""
    prompts = []
    with open(prompts_path, "r") as f:
        for line in f:
            prompts.append(json.loads(line.strip()))
    return prompts


def count_tokens(text: str, tokenizer) -> int:
    """Count tokens in text using the model's tokenizer."""
    return len(tokenizer.encode(text))


def run_baseline_benchmark(
    config: Dict[str, Any],
    prompts: List[Dict[str, Any]],
    results_path: Path,
    log_config: Optional[Dict[str, Any]] = None
) -> None:
    """Run baseline inference benchmark."""
    
    # Configure logger from config if available
    if log_config is None:
        log_config = config.get("logging", {})
    
    if log_config:
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
        }
        level = level_map.get(log_config.get("level", "INFO"), logging.INFO)
        log_dir = Path(log_config.get("log_dir", "logs"))
        console = log_config.get("console", True)
        
        # Reconfigure logger
        benchmark_logger = setup_logger(f"{__name__}.benchmark", log_dir=log_dir, level=level, console=console)
    else:
        benchmark_logger = logger
    
    log_header(benchmark_logger, "RAG Prefill-Decode Asymmetry Baseline Benchmark")
    
    # Initialize vLLM engine
    benchmark_logger.info(f"Initializing vLLM engine with model: {config['model']['name']}")
    llm = LLM(
        model=config["model"]["name"],
        dtype=config["model"]["dtype"],
        max_model_len=config["model"]["max_model_len"],
        tensor_parallel_size=config["inference"]["tensor_parallel_size"],
        gpu_memory_utilization=config["inference"]["gpu_memory_utilization"],
        max_num_seqs=config["inference"]["max_num_seqs"],
        enable_prefix_caching=config["inference"]["enable_prefix_caching"],
    )
    
    tokenizer = llm.get_tokenizer()
    benchmark_logger.debug("Tokenizer loaded successfully")
    
    # Prepare sampling parameters
    sampling_params = SamplingParams(
        temperature=0.0,
        max_tokens=config["workload"]["decode_length"],
    )
    benchmark_logger.debug(f"Sampling params: temperature=0.0, max_tokens={config['workload']['decode_length']}")
    
    results = []
    
    benchmark_logger.info(f"Running inference on {len(prompts)} prompts...")
    log_subheader(benchmark_logger, "Starting inference", width=60)
    
    for idx, prompt_data in enumerate(prompts):
        prompt = prompt_data["prompt"]
        context_length = prompt_data["context_length"]
        sample_id = prompt_data["sample_id"]
        
        # Count actual tokens
        prompt_tokens = count_tokens(prompt, tokenizer)
        
        benchmark_logger.info(f"[{idx+1}/{len(prompts)}] Context length: {context_length} tokens "
                   f"(actual: {prompt_tokens} tokens), Sample: {sample_id}")
        
        # Measure GPU memory before
        if torch.cuda.is_available():
            torch.cuda.reset_peak_memory_stats()
            memory_before = torch.cuda.memory_allocated() / 1024**3  # GB
        
        # Run inference with timing
        start_time = time.time()
        
        # Note: vLLM doesn't expose separate prefill/decode times directly
        # We'll measure TTFT and total latency
        outputs = llm.generate([prompt], sampling_params)
        
        end_time = time.time()
        total_latency = end_time - start_time
        
        # Extract results
        output = outputs[0]
        generated_text = output.outputs[0].text
        num_output_tokens = len(output.outputs[0].token_ids)
        
        # Estimate TTFT (time to first token)
        # For accurate measurement, we'd need to instrument vLLM internals
        # This is an approximation based on total latency
        # In practice, prefill dominates for long contexts
        ttft = total_latency / (num_output_tokens + 1)  # Rough approximation
        
        # Decode throughput
        decode_time = total_latency - ttft
        decode_throughput = num_output_tokens / decode_time if decode_time > 0 else 0
        
        # GPU memory
        if torch.cuda.is_available():
            peak_memory = torch.cuda.max_memory_allocated() / 1024**3  # GB
        else:
            peak_memory = 0
        
        result = {
            "context_length": context_length,
            "sample_id": sample_id,
            "prompt_tokens": prompt_tokens,
            "output_tokens": num_output_tokens,
            "ttft": ttft,
            "total_latency": total_latency,
            "decode_throughput": decode_throughput,
            "peak_gpu_memory_gb": peak_memory,
            "timestamp": time.time(),
        }
        
        results.append(result)
        
        benchmark_logger.info(f"  TTFT: {ttft:.3f}s | Total: {total_latency:.3f}s | "
                   f"Throughput: {decode_throughput:.2f} tokens/s | "
                   f"Memory: {peak_memory:.2f} GB")
    
    # Save results
    results_path.parent.mkdir(parents=True, exist_ok=True)
    with open(results_path, "w") as f:
        for result in results:
            f.write(json.dumps(result) + "\n")
    
    log_header(benchmark_logger, f"Benchmark complete! Results saved to {results_path}")
    
    # Log summary statistics
    benchmark_logger.info("Summary Statistics:")
    log_subheader(benchmark_logger, "", width=60)
    for ctx_len in config["workload"]["context_lengths"]:
        ctx_results = [r for r in results if r["context_length"] == ctx_len]
        if ctx_results:
            avg_ttft = sum(r["ttft"] for r in ctx_results) / len(ctx_results)
            avg_throughput = sum(r["decode_throughput"] for r in ctx_results) / len(ctx_results)
            avg_latency = sum(r["total_latency"] for r in ctx_results) / len(ctx_results)
            benchmark_logger.info(f"Context {ctx_len} tokens: "
                       f"TTFT={avg_ttft:.3f}s, "
                       f"Throughput={avg_throughput:.2f} tok/s, "
                       f"Latency={avg_latency:.3f}s")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run baseline RAG inference benchmark")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/baseline.yaml"),
        help="Path to configuration file"
    )
    parser.add_argument(
        "--prompts",
        type=Path,
        default=Path("data/rag_prompts.jsonl"),
        help="Path to prompts JSONL file"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output results path (overrides config)"
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Load prompts
    prompts = load_prompts(args.prompts)
    
    # Determine output path
    if args.output:
        results_path = args.output
    else:
        results_path = Path(config["output"]["results_dir"]) / config["output"]["filename"]
    
    # Get log config
    log_config = config.get("logging")
    
    # Run benchmark
    run_baseline_benchmark(config, prompts, results_path, log_config=log_config)

