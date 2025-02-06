import logging
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

# Configure the logger

router = APIRouter()


@router.get("/hello-world")
async def hello_world():
    return {"text": "test"}


@router.post("/webhook/twitter", status_code=status.HTTP_200_OK)
async def handle_twitter_webhook(payload: WebhookPayload):
    """
    Endpoint to receive Twitter webhook events.
    """
    try:
        logger.info("Received webhook payload: %s", payload.json())

        # Process the webhook payload using TwitterMonitor
        processed_data = twitter_monitor.handle_webhook(payload.data)

        # TODO: Add further processing logic here (e.g., storing in DB, triggering actions, etc.)

        logger.info("Processed data: %s", processed_data)

        # Respond with a success message
        return JSONResponse(content={"status": "success", "data": processed_data})

    except Exception as e:
        logger.error("Error processing webhook: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )
