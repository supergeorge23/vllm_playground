#!/usr/bin/env python3
"""
Analyze baseline benchmark results.

Reads JSONL result files and generates statistical summaries:
- Average, min, max for key metrics
- Grouped by context length
- Export to CSV or display as table
"""

import argparse
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.utils.logger import setup_logger, log_header

logger = setup_logger(__name__)


def load_results(results_path: Path) -> List[Dict[str, Any]]:
    """Load results from JSONL file."""
    results = []
    with open(results_path, "r") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if line:
                try:
                    results.append(json.loads(line))
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse line {line_num}: {e}")
                    continue
    return results


def analyze_results(results: List[Dict[str, Any]]) -> Dict[int, Dict[str, Any]]:
    """Analyze results grouped by context length."""
    grouped = defaultdict(list)
    
    for result in results:
        ctx_len = result.get("context_length")
        if ctx_len is not None:
            grouped[ctx_len].append(result)
    
    analysis = {}
    
    for ctx_len, ctx_results in sorted(grouped.items()):
        if not ctx_results:
            continue
        
        metrics = {
            "count": len(ctx_results),
            "ttft": {
                "mean": statistics.mean(r["ttft"] for r in ctx_results),
                "min": min(r["ttft"] for r in ctx_results),
                "max": max(r["ttft"] for r in ctx_results),
                "median": statistics.median(r["ttft"] for r in ctx_results),
                "stdev": statistics.stdev([r["ttft"] for r in ctx_results]) if len(ctx_results) > 1 else 0.0,
            },
            "total_latency": {
                "mean": statistics.mean(r["total_latency"] for r in ctx_results),
                "min": min(r["total_latency"] for r in ctx_results),
                "max": max(r["total_latency"] for r in ctx_results),
                "median": statistics.median(r["total_latency"] for r in ctx_results),
            },
            "decode_throughput": {
                "mean": statistics.mean(r["decode_throughput"] for r in ctx_results),
                "min": min(r["decode_throughput"] for r in ctx_results),
                "max": max(r["decode_throughput"] for r in ctx_results),
                "median": statistics.median(r["decode_throughput"] for r in ctx_results),
            },
            "gpu_memory": {
                "mean": statistics.mean(r.get("peak_gpu_memory_gb", 0) for r in ctx_results),
                "max": max(r.get("peak_gpu_memory_gb", 0) for r in ctx_results),
            },
            "prompt_tokens": {
                "mean": statistics.mean(r.get("prompt_tokens", 0) for r in ctx_results),
            },
            "output_tokens": {
                "mean": statistics.mean(r.get("output_tokens", 0) for r in ctx_results),
            },
        }
        
        analysis[ctx_len] = metrics
    
    return analysis


def print_summary_table(analysis: Dict[int, Dict[str, Any]]):
    """Print analysis results as a formatted table."""
    log_header(logger, "Benchmark Results Summary")
    
    # Print TTFT table
    logger.info("\nTime to First Token (TTFT) by Context Length:")
    logger.info("-" * 80)
    logger.info(f"{'Context (tokens)':<20} {'Samples':<10} {'Mean (s)':<12} {'Min (s)':<12} {'Max (s)':<12} {'Median (s)':<12} {'StdDev':<10}")
    logger.info("-" * 80)
    
    for ctx_len in sorted(analysis.keys()):
        m = analysis[ctx_len]
        logger.info(
            f"{ctx_len:<20} "
            f"{m['count']:<10} "
            f"{m['ttft']['mean']:<12.4f} "
            f"{m['ttft']['min']:<12.4f} "
            f"{m['ttft']['max']:<12.4f} "
            f"{m['ttft']['median']:<12.4f} "
            f"{m['ttft']['stdev']:<10.4f}"
        )
    
    # Print throughput table
    logger.info("\nDecode Throughput (tokens/sec) by Context Length:")
    logger.info("-" * 80)
    logger.info(f"{'Context (tokens)':<20} {'Samples':<10} {'Mean':<12} {'Min':<12} {'Max':<12} {'Median':<12}")
    logger.info("-" * 80)
    
    for ctx_len in sorted(analysis.keys()):
        m = analysis[ctx_len]
        logger.info(
            f"{ctx_len:<20} "
            f"{m['count']:<10} "
            f"{m['decode_throughput']['mean']:<12.2f} "
            f"{m['decode_throughput']['min']:<12.2f} "
            f"{m['decode_throughput']['max']:<12.2f} "
            f"{m['decode_throughput']['median']:<12.2f}"
        )
    
    # Print total latency table
    logger.info("\nTotal Latency (s) by Context Length:")
    logger.info("-" * 80)
    logger.info(f"{'Context (tokens)':<20} {'Samples':<10} {'Mean (s)':<12} {'Min (s)':<12} {'Max (s)':<12} {'Median (s)':<12}")
    logger.info("-" * 80)
    
    for ctx_len in sorted(analysis.keys()):
        m = analysis[ctx_len]
        logger.info(
            f"{ctx_len:<20} "
            f"{m['count']:<10} "
            f"{m['total_latency']['mean']:<12.4f} "
            f"{m['total_latency']['min']:<12.4f} "
            f"{m['total_latency']['max']:<12.4f} "
            f"{m['total_latency']['median']:<12.4f}"
        )
    
    # Print GPU memory table
    logger.info("\nGPU Memory Usage by Context Length:")
    logger.info("-" * 80)
    logger.info(f"{'Context (tokens)':<20} {'Mean (GB)':<15} {'Peak (GB)':<15}")
    logger.info("-" * 80)
    
    for ctx_len in sorted(analysis.keys()):
        m = analysis[ctx_len]
        logger.info(
            f"{ctx_len:<20} "
            f"{m['gpu_memory']['mean']:<15.2f} "
            f"{m['gpu_memory']['max']:<15.2f}"
        )


def export_to_csv(analysis: Dict[int, Dict[str, Any]], output_path: Path):
    """Export analysis results to CSV file."""
    import csv
    
    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        
        # Write header
        writer.writerow([
            "context_length", "samples", 
            "ttft_mean", "ttft_min", "ttft_max", "ttft_median", "ttft_stdev",
            "throughput_mean", "throughput_min", "throughput_max", "throughput_median",
            "latency_mean", "latency_min", "latency_max", "latency_median",
            "gpu_memory_mean", "gpu_memory_peak"
        ])
        
        # Write data
        for ctx_len in sorted(analysis.keys()):
            m = analysis[ctx_len]
            writer.writerow([
                ctx_len, m["count"],
                m["ttft"]["mean"], m["ttft"]["min"], m["ttft"]["max"], m["ttft"]["median"], m["ttft"]["stdev"],
                m["decode_throughput"]["mean"], m["decode_throughput"]["min"], m["decode_throughput"]["max"], m["decode_throughput"]["median"],
                m["total_latency"]["mean"], m["total_latency"]["min"], m["total_latency"]["max"], m["total_latency"]["median"],
                m["gpu_memory"]["mean"], m["gpu_memory"]["max"]
            ])
    
    logger.info(f"\nResults exported to CSV: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Analyze baseline benchmark results")
    parser.add_argument(
        "results",
        type=Path,
        help="Path to results JSONL file"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Export to CSV file (optional)"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only output CSV, suppress table display"
    )
    
    args = parser.parse_args()
    
    if not args.results.exists():
        logger.error(f"Results file not found: {args.results}")
        sys.exit(1)
    
    logger.info(f"Loading results from: {args.results}")
    results = load_results(args.results)
    
    if not results:
        logger.error("No valid results found in file")
        sys.exit(1)
    
    logger.info(f"Loaded {len(results)} result entries")
    
    analysis = analyze_results(results)
    
    if not analysis:
        logger.error("No valid analysis data (missing context_length field?)")
        sys.exit(1)
    
    if not args.quiet:
        print_summary_table(analysis)
    
    if args.output:
        export_to_csv(analysis, args.output)
    
    logger.info("\nAnalysis complete!")


if __name__ == "__main__":
    main()
