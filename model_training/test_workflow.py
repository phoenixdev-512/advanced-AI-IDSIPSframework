#!/usr/bin/env python3
"""
Test script to verify model training workflow
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and check for success"""
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"{'='*60}")
    print(f"Command: {cmd}\n")
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ SUCCESS")
        if result.stdout:
            print(result.stdout[-500:])  # Last 500 chars
        return True
    else:
        print("❌ FAILED")
        if result.stderr:
            print(result.stderr[-500:])
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("Model Training Workflow Test")
    print("="*60)
    
    # Create temp directory for test
    test_dir = "/tmp/model_training_test"
    os.makedirs(test_dir, exist_ok=True)
    
    tests = [
        (
            f"python3 model_training/prepare_dataset.py --synthetic --num-flows 1000 --output {test_dir}/data.pkl",
            "Dataset Preparation (Synthetic)"
        ),
        (
            f"python3 model_training/train_basic_models.py --data {test_dir}/data.pkl --output {test_dir}/models/ --model decision_tree",
            "Model Training (Decision Tree)"
        ),
        (
            f"python3 model_training/train_basic_models.py --data {test_dir}/data.pkl --output {test_dir}/models/ --model all",
            "Model Training (All Algorithms)"
        ),
    ]
    
    results = []
    for cmd, desc in tests:
        success = run_command(cmd, desc)
        results.append((desc, success))
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for desc, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {desc}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Model training workflow is working correctly.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
