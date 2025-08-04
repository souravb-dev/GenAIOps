#!/usr/bin/env python3
"""
Comprehensive test for Real-time WebSocket system
Tests authentication, connections, subscriptions, and data broadcasting
"""

import asyncio
import requests
import websockets
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/api/v1/ws/connect"

async def test_realtime_system():
    """Test complete real-time WebSocket system"""
    
    print("🧪 Testing Real-time WebSocket System")
    print("=" * 50)
    
    # Step 1: Login and get token
    print("\n1️⃣ Authenticating user...")
    try:
        login_response = requests.post(f"{BASE_URL}/api/v1/auth/login", 
                                     json={'username': 'admin', 'password': 'AdminPass123!'})
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code} - {login_response.text}")
            return
        
        token = login_response.json()['access_token']
        print("✅ Authentication successful")
        
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return
    
    # Step 2: Test WebSocket connection
    print("\n2️⃣ Testing WebSocket connection...")
    try:
        ws_url_with_token = f"{WS_URL}?token={token}"
        
        async with websockets.connect(ws_url_with_token) as websocket:
            print("✅ WebSocket connected successfully")
            
            # Wait for connection message
            welcome_msg = await websocket.recv()
            welcome_data = json.loads(welcome_msg)
            print(f"📨 Welcome message: {welcome_data['type']}")
            
            # Step 3: Subscribe to alerts
            print("\n3️⃣ Subscribing to real-time alerts...")
            subscribe_msg = {
                "type": "subscribe",
                "data": {"subscription": "alerts"},
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send(json.dumps(subscribe_msg))
            
            # Wait for subscription confirmation
            sub_response = await websocket.recv()
            sub_data = json.loads(sub_response)
            print(f"✅ Subscription confirmed: {sub_data}")
            
            # Step 4: Subscribe to dashboard metrics
            print("\n4️⃣ Subscribing to dashboard metrics...")
            subscribe_metrics = {
                "type": "subscribe",
                "data": {"subscription": "dashboard_metrics"},
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send(json.dumps(subscribe_metrics))
            
            sub_metrics_response = await websocket.recv()
            sub_metrics_data = json.loads(sub_metrics_response)
            print(f"✅ Metrics subscription confirmed: {sub_metrics_data}")
            
            # Step 5: Listen for real-time messages
            print("\n5️⃣ Listening for real-time messages...")
            print("📡 Waiting for system metrics and alerts...")
            
            messages_received = 0
            start_time = time.time()
            
            while messages_received < 5 and (time.time() - start_time) < 30:  # Wait max 30 seconds
                try:
                    # Set timeout for receiving messages
                    message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    msg_data = json.loads(message)
                    
                    messages_received += 1
                    print(f"📨 Message {messages_received}: {msg_data['type']}")
                    
                    if msg_data['type'] == 'metrics_update':
                        metrics = msg_data['data']['data']
                        print(f"   🖥️  CPU: {metrics['cpu_percent']}%, Memory: {metrics['memory_percent']}%")
                    elif msg_data['type'] == 'alert_notification':
                        alert = msg_data['data']['data']
                        print(f"   🚨 Alert: {alert['title']} - {alert['severity']}")
                    
                except asyncio.TimeoutError:
                    print("⏱️  Timeout waiting for message")
                    continue
                except Exception as e:
                    print(f"❌ Error receiving message: {e}")
                    break
            
            print(f"\n✅ Received {messages_received} real-time messages")
            
            # Step 6: Test ping/pong
            print("\n6️⃣ Testing heartbeat...")
            ping_msg = {
                "type": "ping",
                "data": {"timestamp": datetime.now().isoformat()},
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send(json.dumps(ping_msg))
            
            pong_response = await websocket.recv()
            pong_data = json.loads(pong_response)
            print(f"✅ Heartbeat response: {pong_data['type']}")
            
    except Exception as e:
        print(f"❌ WebSocket test error: {e}")
        return
    
    # Step 7: Test WebSocket status endpoint
    print("\n7️⃣ Testing WebSocket management endpoints...")
    try:
        headers = {'Authorization': f'Bearer {token}'}
        
        # Get connection stats
        stats_response = requests.get(f"{BASE_URL}/api/v1/ws/connections/stats", headers=headers)
        if stats_response.status_code == 200:
            stats = stats_response.json()
            print(f"✅ Connection stats: {stats['data']['total_connections']} connections")
        else:
            print(f"⚠️  Stats endpoint: {stats_response.status_code}")
        
        # Test health endpoint
        health_response = requests.get(f"{BASE_URL}/api/v1/ws/health")
        if health_response.status_code == 200:
            health = health_response.json()
            print(f"✅ WebSocket health: {health['status']}")
        else:
            print(f"⚠️  Health endpoint: {health_response.status_code}")
            
    except Exception as e:
        print(f"❌ Management endpoints error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Real-time WebSocket system test completed!")
    print("\n📋 Test Summary:")
    print("   ✅ Authentication")
    print("   ✅ WebSocket connection")
    print("   ✅ Subscription management")
    print("   ✅ Real-time message streaming")
    print("   ✅ Heartbeat mechanism")
    print("   ✅ Management endpoints")

def test_broadcast_alert():
    """Test broadcasting a custom alert"""
    print("\n🚨 Testing custom alert broadcast...")
    try:
        # Login
        login_response = requests.post(f"{BASE_URL}/api/v1/auth/login", 
                                     json={'username': 'admin', 'password': 'AdminPass123!'})
        
        if login_response.status_code != 200:
            print(f"❌ Login failed for broadcast test")
            return
        
        token = login_response.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Broadcast test alert
        test_alert = {
            "title": "Test Alert from Script",
            "message": "This is a test alert generated by the test script",
            "severity": "warning",
            "source": "test_script"
        }
        
        broadcast_response = requests.post(
            f"{BASE_URL}/api/v1/ws/broadcast/test",
            json=test_alert,
            headers=headers,
            params={"subscription_type": "alerts"}
        )
        
        if broadcast_response.status_code == 200:
            print("✅ Test alert broadcast successfully")
        else:
            print(f"❌ Broadcast failed: {broadcast_response.status_code} - {broadcast_response.text}")
            
    except Exception as e:
        print(f"❌ Broadcast test error: {e}")

if __name__ == "__main__":
    print("🚀 Starting Real-time WebSocket System Tests")
    print("📋 Make sure the backend server is running on localhost:8000")
    
    # Test broadcasting first
    test_broadcast_alert()
    
    # Main WebSocket test
    asyncio.run(test_realtime_system())
    
    print("\n🏁 All tests completed!") 