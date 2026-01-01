from abc import ABC, abstractmethod

import httpx

from tailcode.config import Config


class NotificationProvider(ABC):
    @abstractmethod
    def send(self, message: str, title: str | None = None) -> bool:
        pass


class NtfyProvider(NotificationProvider):
    def __init__(self, server: str, topic: str):
        self.server = server.rstrip("/")
        self.topic = topic

    def send(self, message: str, title: str | None = None) -> bool:
        url = f"{self.server}/{self.topic}"
        headers = {}
        if title:
            headers["Title"] = title
        try:
            with httpx.Client() as client:
                response = client.post(url, content=message, headers=headers, timeout=10.0)
                return response.status_code == 200
        except httpx.HTTPError:
            return False


class PushoverProvider(NotificationProvider):
    def __init__(self, app_token: str, user_key: str):
        self.app_token = app_token
        self.user_key = user_key

    def send(self, message: str, title: str | None = None) -> bool:
        data = {
            "token": self.app_token,
            "user": self.user_key,
            "message": message,
        }
        if title:
            data["title"] = title
        try:
            with httpx.Client() as client:
                response = client.post(
                    "https://api.pushover.net/1/messages.json",
                    data=data,
                    timeout=10.0,
                )
                return response.status_code == 200
        except httpx.HTTPError:
            return False


class TelegramProvider(NotificationProvider):
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id

    def send(self, message: str, title: str | None = None) -> bool:
        text = f"*{title}*\n{message}" if title else message
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        try:
            with httpx.Client() as client:
                response = client.post(
                    url,
                    data={"chat_id": self.chat_id, "text": text, "parse_mode": "Markdown"},
                    timeout=10.0,
                )
                return response.status_code == 200
        except httpx.HTTPError:
            return False


def get_notifier(config: Config) -> NotificationProvider:
    provider = config.notifications.provider

    if provider == "ntfy":
        return NtfyProvider(
            server=config.notifications.ntfy.server,
            topic=config.notifications.ntfy.topic,
        )
    elif provider == "pushover":
        return PushoverProvider(
            app_token=config.notifications.pushover.app_token,
            user_key=config.notifications.pushover.user_key,
        )
    elif provider == "telegram":
        return TelegramProvider(
            bot_token=config.notifications.telegram.bot_token,
            chat_id=config.notifications.telegram.chat_id,
        )
    else:
        raise ValueError(f"Unknown notification provider: {provider}")


def notify(message: str, title: str | None = None, config: Config | None = None) -> bool:
    if config is None:
        from tailcode.config import load_config

        config = load_config()

    notifier = get_notifier(config)
    return notifier.send(message, title)
