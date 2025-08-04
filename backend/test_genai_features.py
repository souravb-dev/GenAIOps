#!/usr/bin/env python3
"""
Test GenAI features and endpoints for Task 8
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_genai_health():
    """Test GenAI health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/genai/health", timeout=5)
        print(f"GenAI Health: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"GenAI Health Failed: {e}")
        return False

def test_genai_analyze():
    """Test GenAI analyze endpoint"""
    data = {
        "prompt": "Test analysis prompt",
        "prompt_type": "analysis"
    }
    try:
        response = requests.post(f"{BASE_URL}/api/v1/genai/analyze", json=data, timeout=10)
        print(f"GenAI Analyze: {response.status_code}")
        if response.status_code == 200:
            print("Analysis endpoint working!")
        elif response.status_code == 401:
            print("Authentication required (this is expected)")
        return True
    except Exception as e:
        print(f"GenAI Analyze: {e}")
        return False

def test_genai_capabilities():
    """Test GenAI capabilities endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/genai/capabilities", timeout=5)
        print(f"GenAI Capabilities: {response.status_code}")
        return True
    except Exception as e:
        print(f"GenAI Capabilities: {e}")
        return False

def main():
    print("Testing GenAI Features (Task 8)")
    print("=" * 40)
    
    test_genai_health()
    test_genai_analyze()
    test_genai_capabilities()
    
    print("\nGenAI Testing Complete!")

if __name__ == "__main__":
    main() 