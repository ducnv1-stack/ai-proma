from src.api.logging.logger import get_logger

logger = get_logger(__name__)

async def send_message(events):
    try:
        async for event in events:
            if event.content and event.content.parts and event.content.parts[0].text:
                final_response = event.content.parts[0].text
                yield final_response
                    
    except GeneratorExit:
        logger.info("Generator is being closed")
        raise