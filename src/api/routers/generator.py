from src.api.logging.logger import get_logger
import json
import re
import asyncio
import time

logger = get_logger(__name__)


def hybrid_streaming_split(text):
    """
    Split text into hybrid chunks (3-5 words per chunk) for better streaming
    while maintaining good performance and reducing stuck words
    """
    if not text or not isinstance(text, str):
        return [text]
    
    # Split by sentences first (by punctuation)
    sentences = re.split(r'([.!?]+\s*)', text)
    
    chunks = []
    for sentence in sentences:
        if not sentence.strip():
            continue
            
        # If it's punctuation, add to previous chunk
        if re.match(r'^[.!?]+\s*$', sentence):
            if chunks:
                chunks[-1] += sentence
            continue
        
        # Split sentence into words
        words = sentence.split()
        
        # Group words into chunks of 3-5 words
        for i in range(0, len(words), 4):  # 4 words per chunk (can be 3-5)
            chunk = ' '.join(words[i:i+4])
            if chunk.strip():
                chunks.append(chunk)
    
    return chunks


def chunk_markdown_safe(text, budget_chars=160):
    """
    Split text in a markdown- and punctuation-aware way to avoid
    breaking code blocks and lists. Flushes on sentence boundary or
    when reaching a character budget.
    """
    if not text:
        return []

    buffer = []
    backticks_open = False  # rudimentary inline-code tracking

    def flush():
        chunk = ''.join(buffer)
        buffer.clear()
        return chunk

    chunks = []
    for ch in text:
        buffer.append(ch)
        if ch == '`':
            backticks_open = not backticks_open
        # End conditions when not inside inline code
        if not backticks_open and (ch in ".!?…\n" or len(buffer) >= budget_chars):
            chunk = flush()
            if chunk.strip():
                chunks.append(chunk)

    if buffer:
        chunk = flush()
        if chunk.strip():
            chunks.append(chunk)

    return chunks


def chunk_by_bytes(text, max_bytes=1800):
    """Yield UTF-8 safe chunks with a maximum byte size for SSE stability."""
    if not text:
        return []

    buf = bytearray()
    chunks = []
    for ch in text:
        b = ch.encode("utf-8")
        if len(buf) + len(b) > max_bytes:
            chunks.append(buf.decode("utf-8"))
            buf = bytearray()
        buf.extend(b)
    if buf:
        chunks.append(buf.decode("utf-8"))
    return chunks


def normalize_lists(text):
    """Normalize list formatting so numbered/bullet items start on a new line.
    This does not change semantics, only presentation whitespace.
    """
    if not text:
        return text
    # After sentence end, ensure list markers start on new line
    text = re.sub(r'([.!?…])\s*(\d+\.\s)', r'\1\n\2', text)
    text = re.sub(r'([.!?…])\s*(\*\s)', r'\1\n\2', text)
    # Fix glued pattern like ".2." → ".\n2. "
    text = re.sub(r'([.!?…])(\d+\.)', r'\1\n\2 ', text)
    return text

async def send_message(events):
    try:
        text_buffer = ""
        async for event in events:
            # logger.info(f"[EVENT RAW] {event}")
            if not event.content or not event.content.parts:
                continue
            for part in event.content.parts:
                if hasattr(part, "function_call") and part.function_call is not None:
                    func_call = part.function_call
                    payload = {
                        "function_name": func_call.name,
                        "args": func_call.args or {}
                    }

                    yield "event: thinking\n"
                    yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

                elif hasattr(part, "function_response") and part.function_response is not None:
                    func_resp = part.function_response
                    payload = {
                        "function_name": func_resp.name,
                        "response": func_resp.response or {}
                    }
                    yield "event: execution_tool\n"
                    yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

                elif hasattr(part, "text") and part.text:
                    # Preserve whitespace to avoid glued words during streaming
                    text = part.text
                    if not text or text == "":
                        continue
                    if getattr(event, "partial", False):
                        # ✅ BUFFERED SENTENCE/SEGMENT STREAMING
                        # Accumulate incoming partials, emit only complete segments.
                        text_buffer += text
                        last_emit = time.time()
                        pieces = chunk_markdown_safe(text_buffer, budget_chars=160)
                        # If we got at least one piece and the buffer seems to end
                        # with an incomplete tail (no terminal punctuation/newline),
                        # keep the last piece as remainder.
                        remainder = ""
                        if pieces:
                            # Heuristic: if original buffer does not end with punctuation/newline,
                            # treat last piece as remainder.
                            if not text_buffer.endswith(tuple([".", "!", "?", "…", "\n"])):
                                remainder = pieces[-1]
                                pieces = pieces[:-1]
                        for piece in pieces:
                            piece = normalize_lists(piece)
                            for safe in chunk_by_bytes(piece, max_bytes=1800):
                                elapsed_ms = (time.time() - last_emit) * 1000
                                if elapsed_ms < 40:
                                    await asyncio.sleep((40 - elapsed_ms) / 1000)
                                yield "event: message_chunk\n"
                                yield f"data: {json.dumps(safe, ensure_ascii=False)}\n\n"
                                last_emit = time.time()
                        text_buffer = remainder or (text_buffer if not pieces else (remainder))

        yield "event: stream_end\n"
        # Flush any leftover buffer at the end as a final chunk
        if 'text_buffer' in locals() and text_buffer and text_buffer.strip():
            for safe in chunk_by_bytes(text_buffer, max_bytes=1800):
                yield "event: message_chunk\n"
                yield f"data: {json.dumps(safe, ensure_ascii=False)}\n\n"
        yield "data: {\"done\": true, \"reason\": \"stop\"}\n\n"

    except GeneratorExit:
        yield "event: stream_end\n"
        # Attempt to flush remaining buffer on cancellation
        if 'text_buffer' in locals() and text_buffer and text_buffer.strip():
            for safe in chunk_by_bytes(text_buffer, max_bytes=1800):
                yield "event: message_chunk\n"
                yield f"data: {json.dumps(safe, ensure_ascii=False)}\n\n"
        yield "data: {\"done\": true, \"reason\": \"cancelled\"}\n\n"
        raise
    except Exception as e:
        yield "event: stream_error\n"
        yield f"data: {json.dumps({'error': str(e), 'done': True}, ensure_ascii=False)}\n\n"
        raise
