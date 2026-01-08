#!/usr/bin/env python3
"""
Simple local test for generate_rag_prompts.py

Tests:
1. Generated file format (JSONL)
2. Required fields in each prompt
3. Correct number of prompts
4. Prompt structure and format
5. Context length approximation
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, List


def run_test(test_name: str, test_func):
    """Run a test and report results."""
    print(f"\n{'='*60}")
    print(f"Test: {test_name}")
    print(f"{'='*60}")
    try:
        test_func()
        print(f"✓ PASS: {test_name}")
        return True
    except AssertionError as e:
        print(f"✗ FAIL: {test_name}")
        print(f"  Error: {e}")
        return False
    except Exception as e:
        print(f"✗ ERROR: {test_name}")
        print(f"  Exception: {type(e).__name__}: {e}")
        return False


def test_file_format():
    """Test 1: Verify JSONL file format."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test_prompts.jsonl"
        
        # Run the script
        cmd = [
            sys.executable,
            "scripts/generate_rag_prompts.py",
            "--context-lengths", "100", "200",
            "--num-samples", "3",
            "--output", str(output_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Check file exists
        assert output_path.exists(), "Output file was not created"
        
        # Check file is readable JSONL
        prompts = []
        with open(output_path, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    prompt = json.loads(line)
                    prompts.append(prompt)
        
        assert len(prompts) > 0, "No prompts found in file"
        print(f"  ✓ File created and readable")
        print(f"  ✓ Found {len(prompts)} prompts")


def test_required_fields():
    """Test 2: Verify required fields in each prompt."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test_prompts.jsonl"
        
        cmd = [
            sys.executable,
            "scripts/generate_rag_prompts.py",
            "--context-lengths", "100",
            "--num-samples", "2",
            "--output", str(output_path)
        ]
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        required_fields = ["context_length", "sample_id", "prompt", "query"]
        
        with open(output_path, "r") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line:
                    prompt = json.loads(line)
                    for field in required_fields:
                        assert field in prompt, \
                            f"Missing field '{field}' in prompt at line {line_num}"
                    print(f"  ✓ Line {line_num}: All required fields present")


def test_prompt_count():
    """Test 3: Verify correct number of prompts."""
    context_lengths = [100, 200, 300]
    num_samples = 5
    expected_count = len(context_lengths) * num_samples
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test_prompts.jsonl"
        
        cmd = [
            sys.executable,
            "scripts/generate_rag_prompts.py",
            "--context-lengths"] + [str(cl) for cl in context_lengths] + [
            "--num-samples", str(num_samples),
            "--output", str(output_path)
        ]
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        prompts = []
        with open(output_path, "r") as f:
            for line in f:
                if line.strip():
                    prompts.append(json.loads(line))
        
        assert len(prompts) == expected_count, \
            f"Expected {expected_count} prompts, got {len(prompts)}"
        print(f"  ✓ Generated {len(prompts)} prompts (expected {expected_count})")


def test_prompt_structure():
    """Test 4: Verify prompt structure and format."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test_prompts.jsonl"
        
        cmd = [
            sys.executable,
            "scripts/generate_rag_prompts.py",
            "--context-lengths", "100",
            "--num-samples", "1",
            "--output", str(output_path)
        ]
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        with open(output_path, "r") as f:
            prompt_data = json.loads(f.readline().strip())
        
        prompt_text = prompt_data["prompt"]
        
        # Check prompt contains expected sections
        assert "Context:" in prompt_text, "Prompt missing 'Context:' section"
        assert "Question:" in prompt_text, "Prompt missing 'Question:' section"
        assert "Answer:" in prompt_text, "Prompt missing 'Answer:' section"
        
        # Check query is included
        assert prompt_data["query"] in prompt_text, "Query not found in prompt text"
        
        print(f"  ✓ Prompt structure is correct")
        print(f"  ✓ Contains Context, Question, and Answer sections")


def test_context_length_approximation():
    """Test 5: Verify context length is approximately correct."""
    target_length = 100  # tokens
    # Approximation: ~4 chars per token, so ~400 chars expected
    # Allow some variance: 300-500 chars
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test_prompts.jsonl"
        
        cmd = [
            sys.executable,
            "scripts/generate_rag_prompts.py",
            "--context-lengths", str(target_length),
            "--num-samples", "3",
            "--output", str(output_path)
        ]
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        with open(output_path, "r") as f:
            for line in f:
                if line.strip():
                    prompt_data = json.loads(line)
                    prompt_text = prompt_data["prompt"]
                    
                    # Extract context part (between "Context:" and "Question:")
                    context_start = prompt_text.find("Context:") + len("Context:")
                    context_end = prompt_text.find("Question:")
                    context_text = prompt_text[context_start:context_end].strip()
                    
                    context_chars = len(context_text)
                    expected_min = target_length * 3  # Conservative lower bound
                    expected_max = target_length * 6  # Conservative upper bound
                    
                    assert expected_min <= context_chars <= expected_max, \
                        f"Context length {context_chars} chars not in expected range " \
                        f"[{expected_min}, {expected_max}] for {target_length} tokens"
        
        print(f"  ✓ Context lengths are approximately correct")
        print(f"  ✓ Tested {target_length} tokens → ~{context_chars} chars (expected ~{target_length*4})")


def test_sample_ids():
    """Test 6: Verify sample IDs are correct."""
    num_samples = 5
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test_prompts.jsonl"
        
        cmd = [
            sys.executable,
            "scripts/generate_rag_prompts.py",
            "--context-lengths", "100",
            "--num-samples", str(num_samples),
            "--output", str(output_path)
        ]
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        sample_ids = []
        with open(output_path, "r") as f:
            for line in f:
                if line.strip():
                    prompt_data = json.loads(line)
                    sample_ids.append(prompt_data["sample_id"])
        
        expected_ids = list(range(num_samples))
        assert sample_ids == expected_ids, \
            f"Sample IDs {sample_ids} don't match expected {expected_ids}"
        print(f"  ✓ Sample IDs are correct: {sample_ids}")


def main():
    """Run all tests."""
    print("="*60)
    print("Testing generate_rag_prompts.py")
    print("="*60)
    
    tests = [
        ("File Format", test_file_format),
        ("Required Fields", test_required_fields),
        ("Prompt Count", test_prompt_count),
        ("Prompt Structure", test_prompt_structure),
        ("Context Length Approximation", test_context_length_approximation),
        ("Sample IDs", test_sample_ids),
    ]
    
    results = []
    for test_name, test_func in tests:
        passed = run_test(test_name, test_func)
        results.append((test_name, passed))
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n All tests passed!")
        return 0
    else:
        print(f"\n  {total_count - passed_count} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
