import os

import requests
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field


class PushNotificationInput(BaseModel):
    """ A Message to be sent to the user."""
    message: str = Field(..., description="The message to be sent to the user.")

class PushNotificationTool(BaseTool):
    name: str = "SEnd a push notification"
    description: str = (
        "Clear description for what this tool is useful for, your agent will need this information to use it."
    )
    args_schema: Type[BaseModel] = PushNotificationInput

    def _run(self, message: str) -> str:
        pushover_user = os.environ.get("PUSHOVER_USER")
        pushover_token = os.environ.get("PUSHOVER_TOKEN")
        pushover_url = "http://api.pushover.net/1/messages.json"

        print(f"Push: {message}")
        payload = {"user": pushover_user, "token": pushover_token, "message": message}
        requests.post(url=pushover_url, json=payload)

        return '{notification": "ok"}'
