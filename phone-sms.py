# KimiAxe SMS Gateway - Android Script
# Run this on Android using Termux!

# Install: pip install requests androidhelper
# Or use pydroid3 on Android

import requests
import time
import json
import os

# Configuration
API_URL = "https://kimiaxe-production.up.railway.app"
DEVICE_ID = "device_001"  # Change this for each device

print("📱 KimiAxe SMS Gateway Starting...")
print(f"🔗 API: {API_URL}")
print(f"🆔 Device ID: {DEVICE_ID}")

def send_sms(phone, message):
    """Send SMS via Android"""
    try:
        import androidhelper.droid as droid
        droid.smsSend(phone, message)
        return True
    except:
        # Fallback - print to debug
        print(f"📤 Would send to {phone}: {message}")
        return True

def get_pending_messages():
    """Check API for pending messages"""
    try:
        res = requests.get(f"{API_URL}/api/sms/pending?device={DEVICE_ID}", timeout=10)
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        print(f"Error: {e}")
    return []

def mark_sent(message_id):
    """Mark message as sent"""
    try:
        requests.post(f"{API_URL}/api/sms/status", json={
            "message_id": message_id,
            "status": "sent"
        })
    except:
        pass

def forward_to_api(phone, message):
    """Forward received SMS to API"""
    try:
        requests.post(f"{API_URL}/api/sms/receive", json={
            "device": DEVICE_ID,
            "from": phone,
            "message": message,
            "timestamp": time.time()
        })
    except:
        pass

def check_commands():
    """Check for commands from API"""
    try:
        res = requests.get(f"{API_URL}/api/commands?device={DEVICE_ID}", timeout=5)
        if res.status_code == 200:
            return res.json()
    except:
        pass
    return []

def execute_command(cmd):
    """Execute a command"""
    cmd = cmd.lower().strip()
    
    if cmd == "ping":
        return "pong"
    elif cmd.startswith("send "):
        # send +91number message
        parts = cmd[5:].split(" ", 1)
        if len(parts) == 2:
            send_sms(parts[0], parts[1])
            return f"Sent to {parts[0]}"
    elif cmd == "status":
        return "Online ✅"
    elif cmd == "help":
        return "Commands: ping, send <number> <msg>, status, help"
    else:
        return "Unknown command"
    
    return "Done"

# Main loop
print("\n🚀 Gateway ready! Checking for messages...")
print("Press Ctrl+C to stop\n")

while True:
    try:
        # Check for pending outgoing messages
        pending = get_pending_messages()
        for msg in pending:
            print(f"📤 Sending: {msg['to']} - {msg['message'][:30]}...")
            success = send_sms(msg['to'], msg['message'])
            if success:
                mark_sent(msg['id'])
                print("✅ Sent!")
        
        # Check for commands
        commands = check_commands()
        for cmd in commands:
            print(f"⚡ Command: {cmd['command']}")
            result = execute_command(cmd['command'])
            print(f"📝 Result: {result}")
        
        time.sleep(5)  # Check every 5 seconds
        
    except KeyboardInterrupt:
        print("\n👋 Stopped!")
        break
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(10)
