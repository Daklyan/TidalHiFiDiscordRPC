import json
import os
import time

from enum import Enum
from .baseclient import BaseClient
from .payloads import Payload
from .utils import remove_none, get_event_loop


class Activity(Enum):
    PLAYING = 0
    LISTENING = 2
    WATCHING = 3


class StatusDisplay(Enum):
    NAME = 0
    STATE = 1
    DETAILS = 2


class Presence(BaseClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def update(
        self,
        pid: int = os.getpid(),
        state: str = None,
        details: str = None,
        start: int = None,
        end: int = None,
        large_image: str = None,
        large_text: str = None,
        small_image: str = None,
        small_text: str = None,
        party_id: str = None,
        party_size: list = None,
        join: str = None,
        spectate: str = None,
        match: str = None,
        buttons: list = None,
        instance: bool = True,
        payload_override: dict = None,
        activity_type: int = None,
        status_display_type: int = None,
    ):
        if payload_override is None:
            payload = Payload.set_activity(
                pid=pid,
                state=state,
                details=details,
                start=start,
                end=end,
                large_image=large_image,
                large_text=large_text,
                small_image=small_image,
                small_text=small_text,
                party_id=party_id,
                party_size=party_size,
                join=join,
                spectate=spectate,
                match=match,
                buttons=buttons,
                instance=instance,
                activity=True,
                activity_type=activity_type,
                status_display_type=status_display_type,
            )
        else:
            payload = payload_override
        self.send_data(1, payload)
        return self.loop.run_until_complete(self.read_output())

    def clear(self, pid: int = os.getpid()):
        payload = Payload.set_activity(pid, activity=None)
        self.send_data(1, payload)
        return self.loop.run_until_complete(self.read_output())

    def connect(self):
        self.update_event_loop(get_event_loop())
        self.loop.run_until_complete(self.handshake())

    def close(self):
        self.send_data(2, {"v": 1, "client_id": self.client_id})
        self.sock_writer.close()
        self.loop.close()


class AioPresence(BaseClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, isasync=True)

    async def update(
        self,
        pid: int = os.getpid(),
        state: str = None,
        details: str = None,
        start: int = None,
        end: int = None,
        large_image: str = None,
        large_text: str = None,
        small_image: str = None,
        small_text: str = None,
        party_id: str = None,
        party_size: list = None,
        join: str = None,
        spectate: str = None,
        match: str = None,
        buttons: list = None,
        instance: bool = True,
        activity_type: int = 1,
        status_display_type: int = 1,
    ):
        payload = Payload.set_activity(
            pid=pid,
            state=state,
            details=details,
            start=start,
            end=end,
            large_image=large_image,
            large_text=large_text,
            small_image=small_image,
            small_text=small_text,
            party_id=party_id,
            party_size=party_size,
            join=join,
            spectate=spectate,
            match=match,
            buttons=buttons,
            instance=instance,
            activity=True,
            activity_type=activity_type,
            status_display_type=status_display_type,
        )
        self.send_data(1, payload)
        return await self.read_output()

    async def clear(self, pid: int = os.getpid()):
        payload = Payload.set_activity(pid, activity=None)
        self.send_data(1, payload)
        return await self.read_output()

    async def connect(self):
        self.update_event_loop(get_event_loop())
        await self.handshake()

    def close(self):
        self.send_data(2, {"v": 1, "client_id": self.client_id})
        self.sock_writer.close()
        self.loop.close()
