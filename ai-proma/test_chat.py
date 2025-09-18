#!/usr/bin/env python3
"""Test chat endpoint directly"""

import httpx
import asyncio

async def test_chat():
    """Test chat endpoint with mock token"""
    
    # First login to get token
    login_url = "http://localhost:8006/api/v1/auth/login"
    login_data = {
        "user_name": "a",
        "user_pass": "a"
    }
    
    async with httpx.AsyncClient() as client:
        # Login
        print("🔐 Logging in...")
        login_response = await client.post(login_url, json=login_data)
        print(f"Login status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            token = login_result["access_token"]
            print(f"✅ Got token: {token[:20]}...")
            
            # Test chat
            chat_url = "http://localhost:8006/api/v1/chat"
            chat_data = {
                "message": "Hello test from Python",
                "session_id": "test",
                "workspace_id": "test",
                "agent_id": "project_manager_agent"
            }
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            print("💬 Sending chat request...")
            chat_response = await client.post(chat_url, json=chat_data, headers=headers)
            print(f"Chat status: {chat_response.status_code}")
            
            if chat_response.status_code == 200:
                chat_result = chat_response.json()
                print(f"✅ Chat response: {chat_result['response']}")
            else:
                print(f"❌ Chat error: {chat_response.text}")
        else:
            print(f"❌ Login failed: {login_response.text}")

if __name__ == "__main__":
    asyncio.run(test_chat())
