from __future__ import annotations

from difflib import SequenceMatcher
from pathlib import Path
import re

import pandas as pd


def load_datasheet_kb(file_path: Path) -> list[dict]:
    """
    Đọc datasheet.xlsx và chuyển thành knowledge base dạng list dict.
    """
    if not file_path.exists():
        return []

    # Sheet chính thường là "Tổng hợp"
    try:
        df = pd.read_excel(file_path, sheet_name="Tổng hợp")
    except Exception:
        # Nếu sheet không đúng tên, fallback về sheet đầu tiên
        df = pd.read_excel(file_path)

    df.columns = [str(c).strip() for c in df.columns]

    def norm_col(c: str) -> str:
        return re.sub(r"\s+", "", str(c)).upper()

    def pick_col(need_parts):
        # Tìm cột bằng cách kiểm tra tên cột có chứa các phần (không phân biệt khoảng trắng)
        for c in df.columns:
            cn = norm_col(c)
            if all(part in cn for part in need_parts):
                return c
        return None

    discourse_col = pick_col(["DIỄN", "NGÔN"])
    emotion_col = pick_col(["CẢM", "XÚC"])
    judgement_col = pick_col(["PHÁN", "XÉT"])
    value_col = pick_col(["THẨM", "GIÁ"])

    # Nếu không tìm được cột cốt lõi thì trả về rỗng để app vẫn chạy
    if not discourse_col:
        return []

    kb = []
    for idx, row in df.iterrows():
        discourse = row.get(discourse_col) if discourse_col else None
        if pd.isna(discourse):
            continue

        emotion = row.get(emotion_col) if emotion_col else ""
        judgement = row.get(judgement_col) if judgement_col else ""
        value = row.get(value_col) if value_col else ""
        stt = row.get("STT") if "STT" in df.columns else idx + 1

        kb.append(
            {
                "stt": None if pd.isna(stt) else stt,
                "diễn_ngôn": str(discourse).strip(),
                "cảm_xúc": "" if pd.isna(emotion) else str(emotion).strip(),
                "phán_xét": "" if pd.isna(judgement) else str(judgement).strip(),
                "thẩm_giá": "" if pd.isna(value) else str(value).strip(),
                "diễn_ngôn_norm": str(discourse).strip().lower(),
            }
        )

    return kb


def truncate_text(text: str, max_chars: int = 700) -> str:
    text = str(text).strip()
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(" ", 1)[0] + "..."


def retrieve_datasheet_matches(query: str, kb, top_k: int = 3):
    """
    Chọn dòng liên quan nhất dựa trên:
    - token overlap trên trường diễn_ngôn
    - similarity cơ bản (SequenceMatcher)
    """
    if not kb:
        return []

    q = str(query).lower()
    q_tokens = [t for t in re.split(r"[\W_]+", q) if len(t) >= 3]

    scored = []
    for item in kb:
        hay = item["diễn_ngôn_norm"]
        token_hits = sum(1 for t in q_tokens if t in hay)
        # Giới hạn độ dài phần so sánh để nhanh hơn
        ratio = SequenceMatcher(None, q, hay[:4000]).ratio()
        score = token_hits * 0.9 + ratio
        scored.append((score, item))

    scored.sort(reverse=True, key=lambda x: x[0])
    return [it for _, it in scored[:top_k]]

