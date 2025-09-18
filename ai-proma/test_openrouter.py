#!/usr/bin/env python3
"""Test script to check OpenRouter API connection"""

import httpx
import asyncio
import json
from config import OPENROUTER_API_KEY, DEFAULT_AI_MODEL

async def test_openrouter():
    """Test OpenRouter API directly"""
    
    print("🧪 Testing OpenRouter API...")
    print(f"🔑 API Key: {OPENROUTER_API_KEY[:20]}...{OPENROUTER_API_KEY[-10:]}")
    print(f"🤖 Model: {DEFAULT_AI_MODEL}")
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8004",
        "X-Title": "Proma AI Test"
    }
    
    payload = {
        "model": DEFAULT_AI_MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, can you respond with just 'API test successful'?"}
        ],
        "max_tokens": 50,
        "temperature": 0.7
    }
    
    try:
        async with httpx.AsyncClient() as client:
            print("📡 Sending request to OpenRouter...")
            response = await client.post(url, headers=headers, json=payload, timeout=30.0)
            
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                message = data["choices"][0]["message"]["content"]
                print(f"✅ Success! Response: {message}")
                return True
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"📄 Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"💥 Exception: {str(e)}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_openrouter())
    if result:
        print("\n🎉 OpenRouter API is working!")
    else:
        print("\n💔 OpenRouter API test failed!")
