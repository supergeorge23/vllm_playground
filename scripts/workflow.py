#!/usr/bin/env python3
"""
Main workflow script for RAG prefill-decode asymmetry study.

This script orchestrates the entire workflow:
1. Generate RAG prompts
2. Run baseline inference
3. (Future) Run profiling and optimization experiments
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Optional


def run_command(cmd: list, description: str) -> bool:
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    print(f"Running: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, check=False)
    
    if result.returncode != 0:
        print(f"Error: {description} failed with exit code {result.returncode}")
        return False
    
    print(f"✓ {description} completed successfully")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="RAG Prefill-Decode Asymmetry Workflow"
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/baseline.yaml"),
        help="Path to configuration file"
    )
    parser.add_argument(
        "--phase",
        type=str,
        choices=["1", "2", "3", "all"],
        default="1",
        help="Phase to run: 1=baseline, 2=profiling, 3=optimization, all=all phases"
    )
    parser.add_argument(
        "--skip-prompt-generation",
        action="store_true",
        help="Skip prompt generation (use existing prompts)"
    )
    parser.add_argument(
        "--prompts",
        type=Path,
        default=Path("data/rag_prompts.jsonl"),
        help="Path to prompts file (for generation or loading)"
    )
    
    args = parser.parse_args()
    
    # Phase 1: Baseline Inference
    if args.phase in ["1", "all"]:
        # Generate prompts if needed
        if not args.skip_prompt_generation:
            if not args.prompts.exists():
                print("Generating RAG prompts...")
                generate_cmd = [
                    sys.executable,
                    "scripts/generate_rag_prompts.py",
                    "--output", str(args.prompts),
                ]
                
                # Load config to get context lengths and num_samples
                try:
                    import yaml
                    with open(args.config, "r") as f:
                        config = yaml.safe_load(f)
                    generate_cmd.extend([
                        "--context-lengths"] + 
                        [str(cl) for cl in config["workload"]["context_lengths"]]
                    )
                    generate_cmd.extend([
                        "--num-samples", str(config["workload"]["num_samples"])
                    ])
                except Exception as e:
                    print(f"Warning: Could not load config for prompt generation: {e}")
                    print("Using default parameters")
                
                if not run_command(generate_cmd, "Generate RAG prompts"):
                    sys.exit(1)
            else:
                print(f"Using existing prompts: {args.prompts}")
        
        # Run baseline inference
        baseline_cmd = [
            sys.executable,
            "scripts/run_baseline.py",
            "--config", str(args.config),
            "--prompts", str(args.prompts),
        ]
        
        if not run_command(baseline_cmd, "Run baseline inference benchmark"):
            sys.exit(1)
    
    # Phase 2: Profiling (placeholder)
    if args.phase in ["2", "all"]:
        print("\nPhase 2: Prefill/Decode Profiling")
        print("(Not yet implemented)")
    
    # Phase 3: System Optimization (placeholder)
    if args.phase in ["3", "all"]:
        print("\nPhase 3: System Optimization")
        print("(Not yet implemented)")
    
    print("\n" + "="*60)
    print("Workflow completed!")
    print("="*60)


if __name__ == "__main__":
    main()

