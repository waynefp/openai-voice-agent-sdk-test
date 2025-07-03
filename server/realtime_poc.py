#!/usr/bin/env python3
"""
Proof of Concept: OpenAI Realtime API Connection
This script demonstrates basic connectivity to the OpenAI Realtime API
without modifying the existing Agents SDK implementation.
"""

import asyncio
import json
import os
import websockets
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path="../.env", override=True)

class RealtimeAPIPOC:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.websocket = None
        self.session_id = None

    async def connect(self):
        """Connect to OpenAI Realtime API"""
        uri = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "OpenAI-Beta": "realtime=v1"
        }
        
        print("Connecting to OpenAI Realtime API...")
        try:
            self.websocket = await websockets.connect(uri, extra_headers=headers)
            print("✅ Connected successfully!")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False

    async def send_session_update(self):
        """Configure the session with basic settings"""
        if not self.websocket:
            print("❌ No websocket connection")
            return
            
        session_config = {
            "type": "session.update",
            "session": {
                "modalities": ["text", "audio"],
                "instructions": "You are a helpful assistant for testing the Realtime API. Keep responses brief.",
                "voice": "alloy",
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",
                "turn_detection": {
                    "type": "server_vad",
                    "threshold": 0.5,
                    "prefix_padding_ms": 300,
                    "silence_duration_ms": 200
                },
                "tools": [
                    {
                        "type": "function",
                        "name": "get_current_time",
                        "description": "Get the current time",
                        "parameters": {
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    }
                ]
            }
        }
        
        await self.websocket.send(json.dumps(session_config))
        print("📝 Session configuration sent")

    async def send_text_message(self, text: str):
        """Send a text message to test basic interaction"""
        if not self.websocket:
            print("❌ No websocket connection")
            return
            
        message = {
            "type": "conversation.item.create",
            "item": {
                "type": "message",
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": text
                    }
                ]
            }
        }
        
        await self.websocket.send(json.dumps(message))
        print(f"💬 Sent message: {text}")
        
        # Request a response
        response_request = {
            "type": "response.create",
            "response": {
                "modalities": ["text"]
            }
        }
        await self.websocket.send(json.dumps(response_request))

    async def handle_function_call(self, call_id: str, name: str, arguments: str):
        """Handle function calls from the model"""
        print(f"🔧 Function called: {name} with args: {arguments}")
        
        # Simple function implementation
        if name == "get_current_time":
            import datetime
            result = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            result = "Function not implemented"
        
        function_output = {
            "type": "conversation.item.create",
            "item": {
                "type": "function_call_output",
                "call_id": call_id,
                "output": json.dumps({"result": result})
            }
        }
        
        await self.websocket.send(json.dumps(function_output))
        print(f"✅ Function result sent: {result}")
        
        # Request a response after function execution
        response_request = {"type": "response.create"}
        await self.websocket.send(json.dumps(response_request))

    async def listen_for_events(self):
        """Listen for events from the Realtime API"""
        print("👂 Listening for events...")
        
        try:
            async for message in self.websocket:
                data = json.loads(message)
                event_type = data.get("type")
                
                if event_type == "session.created":
                    self.session_id = data["session"]["id"]
                    print(f"🎉 Session created: {self.session_id}")
                    
                elif event_type == "session.updated":
                    print("⚙️ Session updated successfully")
                    
                elif event_type == "conversation.item.created":
                    item = data.get("item", {})
                    print(f"📄 Conversation item created: {item.get('type')} from {item.get('role', 'unknown')}")
                    
                elif event_type == "response.created":
                    print("🚀 Response generation started")
                    
                elif event_type == "response.text.delta":
                    delta = data.get("delta", "")
                    print(f"📝 Text delta: {delta}", end="", flush=True)
                    
                elif event_type == "response.text.done":
                    print("\n✅ Text response complete")
                    
                elif event_type == "response.audio.delta":
                    audio_data = data.get("delta", "")
                    print(f"🎵 Audio delta received: {len(audio_data)} chars of base64")
                    
                elif event_type == "response.function_call_arguments.done":
                    call_id = data.get("call_id")
                    name = data.get("name")
                    arguments = data.get("arguments", "{}")
                    await self.handle_function_call(call_id, name, arguments)
                    
                elif event_type == "response.done":
                    print("✅ Response generation complete")
                    
                elif event_type == "error":
                    error = data.get("error", {})
                    print(f"❌ Error: {error.get('message', 'Unknown error')}")
                    
                else:
                    print(f"ℹ️ Unhandled event: {event_type}")
                    
        except websockets.exceptions.ConnectionClosed:
            print("🔌 Connection closed")
        except Exception as e:
            print(f"❌ Error listening for events: {e}")

    async def run_test(self):
        """Run the proof of concept test"""
        if not await self.connect():
            return
        
        try:
            # Start listening for events
            listen_task = asyncio.create_task(self.listen_for_events())
            
            # Wait a moment for initial session events
            await asyncio.sleep(1)
            
            # Configure session
            await self.send_session_update()
            await asyncio.sleep(1)
            
            # Send test messages
            test_messages = [
                "Hello! This is a test of the Realtime API.",
                "What time is it?",  # This should trigger the function call
                "Thank you for the test!"
            ]
            
            for message in test_messages:
                await self.send_text_message(message)
                await asyncio.sleep(3)  # Wait for response
            
            # Let it run for a bit more
            await asyncio.sleep(5)
            
        except KeyboardInterrupt:
            print("\n🛑 Test interrupted by user")
        finally:
            if self.websocket:
                await self.websocket.close()
                print("🔌 Connection closed")

async def main():
    """Main function to run the proof of concept"""
    print("🚀 Starting OpenAI Realtime API Proof of Concept")
    print("=" * 50)
    
    poc = RealtimeAPIPOC()
    await poc.run_test()
    
    print("=" * 50)
    print("✅ Proof of concept complete!")

if __name__ == "__main__":
    asyncio.run(main())