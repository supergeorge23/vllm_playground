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

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.utils.logger import setup_logger, log_header

logger = setup_logger(__name__)


def run_command(cmd: list, description: str) -> bool:
    """Run a command and handle errors."""
    log_header(logger, description)
    logger.info(f"Running: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, check=False, capture_output=True, text=True)
    
    # Log stdout and stderr
    if result.stdout:
        logger.debug(f"STDOUT:\n{result.stdout}")
    if result.stderr:
        logger.debug(f"STDERR:\n{result.stderr}")
    
    if result.returncode != 0:
        logger.error(f"{description} failed with exit code {result.returncode}")
        if result.stderr:
            logger.error(f"Error output: {result.stderr}")
        return False
    
    logger.info(f"✓ {description} completed successfully")
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
    
    log_header(logger, "RAG Prefill-Decode Asymmetry Workflow")
    logger.info(f"Configuration: {args.config}")
    logger.info(f"Phase: {args.phase}")
    
    # Phase 1: Baseline Inference
    if args.phase in ["1", "all"]:
        logger.info("Starting Phase 1: Baseline Inference")
        
        # Generate prompts if needed
        if not args.skip_prompt_generation:
            if not args.prompts.exists():
                logger.info("Generating RAG prompts...")
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
                    logger.debug(f"Loaded config: context_lengths={config['workload']['context_lengths']}, "
                               f"num_samples={config['workload']['num_samples']}")
                except Exception as e:
                    logger.warning(f"Could not load config for prompt generation: {e}")
                    logger.info("Using default parameters")
                
                if not run_command(generate_cmd, "Generate RAG prompts"):
                    logger.error("Failed to generate prompts. Exiting.")
                    sys.exit(1)
            else:
                logger.info(f"Using existing prompts: {args.prompts}")
        
        # Run baseline inference
        baseline_cmd = [
            sys.executable,
            "scripts/run_baseline.py",
            "--config", str(args.config),
            "--prompts", str(args.prompts),
        ]
        
        if not run_command(baseline_cmd, "Run baseline inference benchmark"):
            logger.error("Baseline inference failed. Exiting.")
            sys.exit(1)
        
        logger.info("Phase 1 completed successfully")
    
    # Phase 2: Profiling (placeholder)
    if args.phase in ["2", "all"]:
        logger.info("Phase 2: Prefill/Decode Profiling")
        logger.warning("Phase 2 not yet implemented")
    
    # Phase 3: System Optimization (placeholder)
    if args.phase in ["3", "all"]:
        logger.info("Phase 3: System Optimization")
        logger.warning("Phase 3 not yet implemented")
    
    log_header(logger, "Workflow completed!")


if __name__ == "__main__":
    main()

