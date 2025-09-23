from src.api.logging.logger import get_logger
import json

logger = get_logger(__name__)


async def send_message(events):
    try:
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
                    text = part.text.strip()
                    if not text:
                        continue
                    if getattr(event, "partial", False):
                        yield f"event: message_chunk\n"
                        yield f"data: {json.dumps(text, ensure_ascii=False)}\n\n"

        yield "event: stream_end\n"
        yield "data: {\"done\": true, \"reason\": \"stop\"}\n\n"

    except GeneratorExit:
        yield "event: stream_end\n"
        yield "data: {\"done\": true, \"reason\": \"cancelled\"}\n\n"
        raise
    except Exception as e:
        yield "event: stream_error\n"
        yield f"data: {json.dumps({'error': str(e), 'done': True}, ensure_ascii=False)}\n\n"
        raise
