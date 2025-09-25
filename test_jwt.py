#!/usr/bin/env python3
"""
Test script để demo JWT đơn giản cho AI-Proma
"""

import requests
import json

# Base URL của API
BASE_URL = "http://localhost:8000"

def test_create_jwt():
    """Test tạo JWT token với thông tin bất kỳ"""
    print("=== TEST TẠO JWT TOKEN ===")
    
    url = f"{BASE_URL}/api/v1/auth/token"
    payload = {
        "workspace_id": "963c2754-6388-4219-8989-39bb5d12ade",
        "user_id": "65cd8c30-5300-4b73-a9fa-add929ad6fd8",
        "username": "XCEL_BOT",
        "role": "user",
        "extra_field": "this will be ignored",
        "another_field": "also ignored"
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            print("✅ Tạo token thành công!")
            print(f"Token: {data['access_token'][:50]}...")
            print(f"Claims: {json.dumps(data['claims'], indent=2)}")
            return data['access_token']
        else:
            print(f"❌ Lỗi: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def test_decode_jwt(token):
    """Test decode JWT token"""
    print("\n=== TEST DECODE JWT TOKEN ===")
    
    url = f"{BASE_URL}/api/v1/auth/decode"
    
    try:
        response = requests.post(url, params={"token": token})
        if response.status_code == 200:
            data = response.json()
            print("✅ Decode token thành công!")
            print(f"Payload: {json.dumps(data['payload'], indent=2)}")
            print(f"Expires at: {data['expires_at']}")
        else:
            print(f"❌ Lỗi: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")

def test_create_epic_with_jwt(token):
    """Test tạo epic với JWT token đã cải tiến"""
    print("\n=== TEST TẠO EPIC VỚI JWT CẢI TIẾN ===")
    
    url = f"{BASE_URL}/api/v1/epics/create"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "epic_name": "Epic từ JWT cải tiến",
        "description": "Epic được tạo từ JWT chỉ cần workspace_id, user_id, user_name",
        "category": "Development",
        "priority": "High"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print("✅ Tạo epic thành công!")
            print(f"Epic ID: {data.get('epic', {}).get('epic_id')}")
            print(f"Epic Name: {data.get('epic', {}).get('epic_name')}")
        else:
            print(f"❌ Lỗi: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    print("🚀 Testing JWT System cho AI-Proma")
    print("=" * 50)
    
    # 1. Tạo JWT token
    token = test_create_jwt()
    
    if token:
        # 2. Decode JWT token
        test_decode_jwt(token)
        
        # 3. Test tạo epic với JWT
        test_create_epic_with_jwt(token)
    
    print("\n✨ Test hoàn thành!")
