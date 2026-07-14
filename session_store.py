"""
session_store.py — 会话持久化模块（JSON 文件存储）

功能：
  - 创建新会话
  - 追加消息到会话
  - 读取历史会话
  - 列出所有会话
  - 清除过期会话
V2 新增：JSON 文件持久化，重启不丢失
"""

import json
import os
import uuid
from typing import List, Optional
from datetime import datetime
from models.schema import SessionRecord


# 会话存储目录
SESSION_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sessions")


def _ensure_dir():
    """确保会话存储目录存在"""
    os.makedirs(SESSION_DIR, exist_ok=True)


def _session_file_path(session_id: str) -> str:
    return os.path.join(SESSION_DIR, f"{session_id}.json")


def create_session() -> str:
    """创建新会话，返回 session_id"""
    _ensure_dir()
    session_id = str(uuid.uuid4())[:8]
    now = datetime.now().isoformat()
    record = SessionRecord(
        session_id=session_id,
        messages=[],
        created_at=now,
        updated_at=now,
    )
    with open(_session_file_path(session_id), "w", encoding="utf-8") as f:
        json.dump(record.model_dump(), f, ensure_ascii=False, indent=2)
    return session_id


def append_message(session_id: str, role: str, content: str, agent: Optional[str] = None):
    """向会话追加一条消息"""
    _ensure_dir()
    filepath = _session_file_path(session_id)
    if not os.path.exists(filepath):
        record = SessionRecord(
            session_id=session_id,
            messages=[],
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )
    else:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        record = SessionRecord(**data)

    record.messages.append({
        "role": role,
        "content": content,
        "agent": agent,
        "timestamp": datetime.now().isoformat(),
    })
    record.updated_at = datetime.now().isoformat()

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(record.model_dump(), f, ensure_ascii=False, indent=2)


def get_session(session_id: str) -> Optional[SessionRecord]:
    """获取会话历史"""
    filepath = _session_file_path(session_id)
    if not os.path.exists(filepath):
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        return SessionRecord(**json.load(f))


def list_sessions(limit: int = 20) -> List[SessionRecord]:
    """列出最近的会话"""
    _ensure_dir()
    files = [
        f for f in os.listdir(SESSION_DIR)
        if f.endswith(".json")
    ]
    sessions = []
    for f in files:
        filepath = os.path.join(SESSION_DIR, f)
        try:
            with open(filepath, "r", encoding="utf-8") as fp:
                data = json.load(fp)
            sessions.append(SessionRecord(**data))
        except Exception:
            continue

    sessions.sort(key=lambda s: s.updated_at, reverse=True)
    return sessions[:limit]


def delete_session(session_id: str) -> bool:
    """删除指定会话"""
    filepath = _session_file_path(session_id)
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False


def clear_old_sessions(days: int = 7):
    """清除超过指定天数的会话"""
    _ensure_dir()
    now = datetime.now()
    for f in os.listdir(SESSION_DIR):
        if not f.endswith(".json"):
            continue
        filepath = os.path.join(SESSION_DIR, f)
        try:
            with open(filepath, "r", encoding="utf-8") as fp:
                data = json.load(fp)
            updated = datetime.fromisoformat(data.get("updated_at", ""))
            if (now - updated).days > days:
                os.remove(filepath)
        except Exception:
            os.remove(filepath)
