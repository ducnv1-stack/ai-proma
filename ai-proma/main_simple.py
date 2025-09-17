# Import mock Google ADK first
import mock_google_adk

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
from contextlib import asynccontextmanager
import logging
import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv("config.env")

# Initialize OpenAI client
openai_client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
)

# Simple lifespan manager without database
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting FARAMEX...")
    yield
    print("Shutting down FARAMEX...")

# Create FastAPI app
app = FastAPI(
    title="FARAMEX AI Server",
    description="AI Multi-Agent System with Chat Interface",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for frontend
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# Simple chat endpoint for demo
from fastapi import HTTPException
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
import asyncio
import json

class ChatMessage(BaseModel):
    message: str
    session_id: str = "demo-session"

@app.post("/api/v1/chat")
async def chat_demo(data: ChatMessage):
    """Demo chat endpoint with mock streaming response"""
    
    async def generate_response():
        try:
            # Check if OpenAI API key is configured
            if not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") == "your_openai_api_key_here":
                # Fallback to mock response if API key not configured
                responses = [
                    "⚠️ OpenAI API key chưa được cấu hình.",
                    " Vui lòng cập nhật OPENAI_API_KEY trong file config.env",
                    " để sử dụng model gpt-4o-mini.",
                    f" Tin nhắn của bạn: '{data.message}'"
                ]
                
                for i, response_part in enumerate(responses):
                    await asyncio.sleep(0.5)  # Faster mock response
                    event_data = {
                        "content": response_part,
                        "session_id": data.session_id,
                        "message_id": f"msg_{i}",
                        "timestamp": "2024-01-01T00:00:00Z"
                    }
                    yield f"data: {json.dumps(event_data)}\n\n"
                
                yield f"data: [DONE]\n\n"
                return

            # Create OpenAI chat completion with streaming
            system_message = """Bạn là FARAMEX Marketing Agent - chuyên gia marketing Facebook thông minh và chuyên nghiệp. 
            Bạn có thể giúp khách hàng với:
            - Tạo chiến lược marketing Facebook hiệu quả
            - Viết nội dung quảng cáo hấp dẫn
            - Phân tích và tối ưu hóa hiệu suất campaign
            - Tư vấn về targeting và budget allocation
            - Đưa ra insights về trends và best practices
            
            Hãy trả lời bằng tiếng Việt một cách thân thiện và chuyên nghiệp."""

            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": data.message}
            ]

            # Stream response from OpenAI with optimized settings
            stream = await openai_client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                messages=messages,
                stream=True,
                temperature=0.3,  # Lower temperature for faster, more focused responses
                max_tokens=1500,  # Increased for more complete responses
                top_p=0.9,       # Nucleus sampling for better quality
                frequency_penalty=0.1,  # Reduce repetition
                presence_penalty=0.1    # Encourage diverse responses
            )

            message_id = 0
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    
                    event_data = {
                        "content": content,
                        "session_id": data.session_id,
                        "message_id": f"msg_{message_id}",
                        "timestamp": "2024-01-01T00:00:00Z"
                    }
                    
                    yield f"data: {json.dumps(event_data)}\n\n"
                    message_id += 1

            # End of stream
            yield f"data: [DONE]\n\n"

        except Exception as e:
            # Error handling
            error_message = f"Lỗi khi gọi OpenAI API: {str(e)}"
            event_data = {
                "content": error_message,
                "session_id": data.session_id,
                "message_id": "error",
                "timestamp": "2024-01-01T00:00:00Z"
            }
            yield f"data: {json.dumps(event_data)}\n\n"
            yield f"data: [DONE]\n\n"
    
    return StreamingResponse(
        generate_response(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "*"
        }
    )

@app.get("/api/v1/agents")
async def get_agents():
    """Demo agents endpoint"""
    return {
        "agents": [
            {
                "id": "facebook_marketing_agent",
                "name": "Facebook Marketing Agent",
                "description": "Chuyên gia marketing Facebook với khả năng tạo nội dung, phân tích và tối ưu hóa chiến dịch",
                "status": "active"
            }
        ]
    }

@app.post("/api/v1/session/create")
async def create_session():
    """Demo session creation endpoint"""
    return {
        "session_id": "demo-session-123",
        "status": "created",
        "agent_id": "facebook_marketing_agent"
    }

@app.get("/")
async def root():
    """Root endpoint redirect to demo page"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/frontend/demo.html")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "FARAMEX AI Server is running"}

if __name__ == "__main__":
    print("Starting FARAMEX AI Server (Demo Mode)")
    print("Frontend: http://localhost:8000/frontend/")
    print("Demo Page: http://localhost:8000/frontend/demo.html")
    print("Chat Interface: http://localhost:8000/frontend/index.html")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
