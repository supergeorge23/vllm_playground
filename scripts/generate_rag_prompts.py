#!/usr/bin/env python3
"""
Generate synthetic RAG prompts for benchmarking.

Creates prompts with:
- Long RAG context (variable length)
- Short user query
- Expected short decode output
"""

import argparse
import json
import random
from pathlib import Path
from typing import List, Dict


def generate_rag_context(length_tokens: int) -> str:
    """
    Generate a synthetic RAG context of approximately the specified token length.
    Note: This is a simple approximation. For accurate token counting, use the model's tokenizer.
    """
    # Simple approximation: ~4 characters per token
    target_chars = length_tokens * 4
    
    # Generate synthetic document-like text
    paragraphs = []
    current_length = 0
    
    topics = [
        "machine learning", "neural networks", "transformer architecture",
        "attention mechanisms", "language models", "retrieval augmented generation",
        "vector databases", "embedding models", "semantic search",
        "knowledge graphs", "information retrieval", "natural language processing"
    ]
    
    while current_length < target_chars:
        topic = random.choice(topics)
        paragraph = f"""
The field of {topic} has seen significant advances in recent years. 
Researchers have developed novel approaches that combine multiple techniques 
to achieve state-of-the-art performance. These methods leverage large-scale 
datasets and computational resources to train models that can understand 
and generate human-like text. The key innovation lies in the ability to 
process and reason over vast amounts of information efficiently.
"""
        paragraphs.append(paragraph)
        current_length += len(paragraph)
    
    return "\n".join(paragraphs)


def generate_query() -> str:
    """Generate a short user query."""
    queries = [
        "What are the main findings?",
        "Summarize the key points.",
        "What is the conclusion?",
        "Explain the main idea.",
        "What are the important details?",
        "Give me a brief overview.",
        "What does this tell us?",
        "What is the summary?",
    ]
    return random.choice(queries)


def create_rag_prompt(context: str, query: str) -> str:
    """Format a RAG prompt with context and query."""
    return f"""Context:
{context}

Question: {query}

Answer:"""


def generate_prompts(
    context_lengths: List[int],
    query_length: int,
    num_samples: int,
    output_path: Path
) -> None:
    """Generate RAG prompts for all specified context lengths."""
    prompts = []
    
    for ctx_len in context_lengths:
        for sample_idx in range(num_samples):
            context = generate_rag_context(ctx_len)
            query = generate_query()
            prompt = create_rag_prompt(context, query)
            
            prompts.append({
                "context_length": ctx_len,
                "sample_id": sample_idx,
                "prompt": prompt,
                "query": query,
            })
    
    # Save to JSONL
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        for prompt in prompts:
            f.write(json.dumps(prompt) + "\n")
    
    print(f"Generated {len(prompts)} prompts saved to {output_path}")
    print(f"Context lengths: {context_lengths}")
    print(f"Samples per length: {num_samples}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate synthetic RAG prompts")
    parser.add_argument(
        "--context-lengths",
        type=int,
        nargs="+",
        default=[2048, 4096, 8192, 16384],
        help="Context lengths in tokens"
    )
    parser.add_argument(
        "--num-samples",
        type=int,
        default=10,
        help="Number of samples per context length"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/rag_prompts.jsonl"),
        help="Output file path"
    )
    
    args = parser.parse_args()
    generate_prompts(
        context_lengths=args.context_lengths,
        query_length=50,  # Not used in current implementation
        num_samples=args.num_samples,
        output_path=args.output
    )

