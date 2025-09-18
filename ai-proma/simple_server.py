#!/usr/bin/env python3
"""
Simple HTTP Server for Proma AI - No external dependencies required
"""
import http.server
import socketserver
import json
import urllib.parse
import os
from datetime import datetime

class PromaHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="frontend", **kwargs)
    
    def do_GET(self):
        if self.path == '/':
            self.path = '/dashboard.html'
        elif self.path == '/demo':
            self.path = '/demo.html'
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                "status": "healthy",
                "message": "Proma AI Server is running",
                "timestamp": datetime.now().isoformat()
            }
            self.wfile.write(json.dumps(response).encode())
            return
        elif self.path == '/api/v1/agents':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                "agents": [
                    {
                        "id": "project_manager_agent",
                        "name": "Proma Project Manager Agent",
                        "description": "Chuyên gia quản lý dự án, có thể tạo các task, giao việc cho các agent khác",
                        "status": "active"
                    }
                ]
            }
            self.wfile.write(json.dumps(response).encode())
            return
        
        super().do_GET()
    
    def do_POST(self):
        if self.path == '/api/v1/chat':
            self.send_response(200)
            self.send_header('Content-type', 'text/event-stream')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Connection', 'keep-alive')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Headers', '*')
            self.send_header('Access-Control-Allow-Methods', '*')
            self.end_headers()
            
            # Mock streaming response
            responses = [
                "Xin chào! Tôi là Proma Project Manager Agent.",
                " Tôi có thể giúp bạn quản lý dự án hiệu quả.",
                " Bạn cần hỗ trợ gì về quản lý dự án hôm nay?"
            ]
            
            for i, response_part in enumerate(responses):
                event_data = {
                    "content": response_part,
                    "session_id": "demo-session",
                    "message_id": f"msg_{i}",
                    "timestamp": datetime.now().isoformat()
                }
                self.wfile.write(f"data: {json.dumps(event_data)}\n\n".encode())
                self.wfile.flush()
            
            self.wfile.write(b"data: [DONE]\n\n")
            return
        elif self.path == '/api/v1/session/create':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                "session_id": "demo-session-123",
                "status": "created",
                "agent_id": "project_manager_agent"
            }
            self.wfile.write(json.dumps(response).encode())
            return
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()

if __name__ == "__main__":
    PORT = 8000
    
    print("🚀 Starting Proma AI Server (Simple Mode)")
    print(f"📱 Frontend: http://localhost:{PORT}/")
    print(f"🎮 Demo Page: http://localhost:{PORT}/demo.html")
    print(f"💬 Chat Interface: http://localhost:{PORT}/index.html")
    print(f"📊 Dashboard: http://localhost:{PORT}/dashboard.html")
    print("✅ Server is ready!")
    
    with socketserver.TCPServer(("", PORT), PromaHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped by user")
