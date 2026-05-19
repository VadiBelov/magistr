from fastapi import WebSocket
from typing import Dict, List
import json


class RoomManager:
    def __init__(self):
        self.rooms: Dict[str, Dict[str, List[WebSocket]]] = {}
        self.transcripts: Dict[str, List[dict]] = {}

    def create_room(self, room_id: str):
        if room_id not in self.rooms:
            self.rooms[room_id] = {}
            self.transcripts[room_id] = []
        return room_id

    async def join_room(self, room_id: str, user_id: str, ws: WebSocket):
        self.create_room(room_id)
        if user_id not in self.rooms[room_id]:
            self.rooms[room_id][user_id] = []
        self.rooms[room_id][user_id].append(ws)
        await self.broadcast_participants(room_id)

    async def leave_room(self, room_id: str, user_id: str, ws: WebSocket):
        if room_id in self.rooms and user_id in self.rooms[room_id]:
            if ws in self.rooms[room_id][user_id]:
                self.rooms[room_id][user_id].remove(ws)
            if not self.rooms[room_id][user_id]:
                del self.rooms[room_id][user_id]
        await self.broadcast_participants(room_id)

    async def broadcast_transcript(self, room_id: str, segment: dict):
        if room_id in self.transcripts:
            self.transcripts[room_id].append(segment)

        if room_id in self.rooms:
            message = json.dumps({"type": "transcript", "segment": segment})
            for connections in self.rooms[room_id].values():
                for ws in connections:
                    try:
                        await ws.send_text(message)
                    except:
                        pass

    async def broadcast_participants(self, room_id: str):
        if room_id in self.rooms:
            participants = list(self.rooms[room_id].keys())
            message = json.dumps({"type": "participants", "participants": participants})
            for connections in self.rooms[room_id].values():
                for ws in connections:
                    try:
                        await ws.send_text(message)
                    except:
                        pass

    async def broadcast_chat(self, room_id: str, author: str, text: str):
        if room_id in self.rooms:
            message = json.dumps({"type": "chat", "author": author, "text": text})
            for connections in self.rooms[room_id].values():
                for ws in connections:
                    try:
                        await ws.send_text(message)
                    except:
                        pass

    def get_transcript(self, room_id: str) -> List[dict]:
        return self.transcripts.get(room_id, [])


manager = RoomManager()