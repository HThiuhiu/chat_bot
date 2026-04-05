import base64
import html
import re
from pathlib import Path
from urllib.parse import quote_plus

import google.generativeai as genai
import streamlit as st

from src.datasheet_rag import (
    load_datasheet_kb as _load_datasheet_kb,
    retrieve_datasheet_matches as _retrieve_datasheet_matches,
    truncate_text as _truncate_text,
)
from src.prompts import SYSTEM_INSTRUCTION


st.set_page_config(page_title="Ra mắt Aura - Chatbot AI", page_icon="🦉", layout="wide")


def read_ui_text(filename: str) -> str:
    ui_path = Path(__file__).resolve().parent / "ui" / filename
    return ui_path.read_text(encoding="utf-8")


def compact_html(raw_html: str) -> str:
    return re.sub(r">\s+<", "><", raw_html.strip())


def image_to_data_uri(relative_path: str) -> str:
    image_path = Path(__file__).resolve().parent / "ui" / relative_path
    mime_type = "image/jpeg" if image_path.suffix.lower() in {".jpg", ".jpeg"} else "image/png"
    encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def render_chat_content(role: str, content: str) -> None:
    safe_content = html.escape(str(content)).replace("\n", "<br>")
    st.markdown(
        f'<div class="chat-copy chat-copy-{role}">{safe_content}</div>',
        unsafe_allow_html=True,
    )


page_bg_uri = image_to_data_uri("assets/bia.jpg")
assistant_avatar_uri = image_to_data_uri("assets/ai3.png")
user_avatar_uri = image_to_data_uri("assets/nguoi3.png")
styles_css = read_ui_text("styles.css").replace("{{PAGE_BG}}", page_bg_uri)
st.markdown(f"<style>\n{styles_css}\n</style>", unsafe_allow_html=True)

app_url = st.secrets.get("APP_URL", "https://chatbot-zuckxrzzsttqfgqedvwat3.streamlit.app/").strip()
qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=160x160&data={quote_plus(app_url)}"
st.markdown(compact_html(read_ui_text("education_line.html")), unsafe_allow_html=True)

hero_html = read_ui_text("hero.html").replace("{{QR_URL}}", qr_url)
st.markdown(compact_html(hero_html), unsafe_allow_html=True)

showcase_html = read_ui_text("showcase.html").replace("{{QR_URL}}", qr_url)
st.markdown(compact_html(showcase_html), unsafe_allow_html=True)

try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except KeyError:
    st.error("Lỗi: Chưa cấu hình API key trong file secrets.toml")
    st.stop()


MODEL_NAME = st.secrets.get("GEMINI_MODEL", "gemini-2.5-flash").strip()
MAX_OUTPUT_TOKENS = int(st.secrets.get("MAX_OUTPUT_TOKENS", 220))
RAG_TOP_K = int(st.secrets.get("RAG_TOP_K", 1))
CHAT_HISTORY_TURNS = int(st.secrets.get("CHAT_HISTORY_TURNS", 2))
STREAM_UPDATE_EVERY = max(1, int(st.secrets.get("STREAM_UPDATE_EVERY", 3)))


@st.cache_data(show_spinner=False)
def load_datasheet_kb():
    file_path = Path(__file__).resolve().parent / "datasheet.xlsx"
    return _load_datasheet_kb(file_path)


def truncate_text(text: str, max_chars: int = 700) -> str:
    return _truncate_text(text, max_chars)


def retrieve_datasheet_matches(query: str, kb, top_k: int = 3):
    return _retrieve_datasheet_matches(query, kb, top_k)


def build_private_reference_context(matches: list[dict]) -> str:
    if not matches:
        return ""

    context_lines = [
        "Ngữ cảnh tham khảo nội bộ dưới đây chỉ dùng để hiểu mẫu cảm xúc và cách gợi mở.",
        "Tuyệt đối không nhắc đến nguồn, tên file, STT, mã số, hay nói rằng đang tham chiếu dữ liệu.",
        "Nếu sử dụng ý từ các mục này, hãy diễn đạt lại thành nhận định tổng quát, không nêu ví dụ nhận dạng được.",
    ]

    for idx, match in enumerate(matches, start=1):
        context_lines.append(
            f"- Mẫu tham khảo {idx}:\n"
            f"  Diễn ngôn: {truncate_text(match['diễn_ngôn'], 600)}\n"
            f"  Cảm xúc: {truncate_text(match['cảm_xúc'], 300)}\n"
            f"  Phán xét: {truncate_text(match['phán_xét'], 300)}\n"
            f"  Thẩm giá: {truncate_text(match['thẩm_giá'], 300)}"
        )

    return "\n".join(context_lines)


def sanitize_model_response(text: str) -> str:
    cleaned = str(text)
    substitutions = [
        (r"\bSTT\s*[:\-]?\s*\d+\b", ""),
        (r"\bdatasheet\.xlsx\b", "nguồn nội bộ"),
        (r"\bdataset\b", "nguồn tham khảo"),
        (r"\bbộ dữ liệu\b", "nguồn tham khảo"),
        (r"\bdữ liệu tham khảo\b", "nguồn tham khảo"),
        (r"\btheo dữ liệu\b[:,]?\s*", ""),
        (r"\btheo nguồn nội bộ\b[:,]?\s*", ""),
        (r"\btheo nguồn tham khảo\b[:,]?\s*", ""),
        (r"\btrong datasheet\.xlsx\b[:,]?\s*", ""),
    ]
    for pattern, replacement in substitutions:
        cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)

    cleaned = re.sub(r"\([^\)]*\bSTT\b[^\)]*\)", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def build_recent_history(ui_messages: list[dict], max_turns: int) -> list[dict]:
    if max_turns <= 0:
        return []

    return ui_messages[-(max_turns * 2):]


def build_recent_history_text(ui_messages: list[dict], max_turns: int) -> str:
    recent_messages = build_recent_history(ui_messages, max_turns)
    if not recent_messages:
        return ""

    lines = ["Ngữ cảnh hội thoại gần nhất:"]
    for message in recent_messages:
        speaker = "Aura" if message["role"] == "assistant" else "Bạn"
        lines.append(f"{speaker}: {truncate_text(message['content'], 180)}")
    return "\n".join(lines)


def should_use_rag(query: str) -> bool:
    normalized = query.strip().lower()
    if len(normalized) <= 40:
        return False

    keywords = (
        "trường",
        "ngành",
        "học",
        "điểm",
        "xét tuyển",
        "học phí",
        "tư vấn",
        "thông tin",
        "ngành học",
        "đại học",
        "cao đẳng",
    )
    return any(keyword in normalized for keyword in keywords)


generation_config = genai.GenerationConfig(
    temperature=0.55,
    top_p=0.95,
    max_output_tokens=MAX_OUTPUT_TOKENS,
)
model = genai.GenerativeModel(
    model_name=MODEL_NAME,
    generation_config=generation_config,
    system_instruction=SYSTEM_INSTRUCTION,
)

if "ui_messages" not in st.session_state:
    st.session_state.ui_messages = []


st.markdown('<div class="chat-entry-label">Bắt đầu trò chuyện với Aura tại đây</div>', unsafe_allow_html=True)

if st.button("🗑️ Xóa cuộc trò chuyện để bắt đầu lại"):
    st.session_state.pop("ui_messages", None)
    st.rerun()

chat_container = st.container()
with chat_container:
    for message in st.session_state.ui_messages:
        role = message["role"]
        avatar = assistant_avatar_uri if role == "assistant" else user_avatar_uri
        with st.chat_message(role, avatar=avatar):
            render_chat_content(role, message["content"])

datasheet_kb = load_datasheet_kb()

if prompt := st.chat_input("Hôm nay của bạn thế nào? Hãy kể Aura nghe nhé..."):
    st.session_state.ui_messages.append({"role": "user", "content": prompt})
    with chat_container:
        with st.chat_message("user", avatar=user_avatar_uri):
            render_chat_content("user", prompt)
        with st.chat_message("assistant", avatar=assistant_avatar_uri):
            message_placeholder = st.empty()
            full_response = ""
            try:
                matches = []
                if datasheet_kb and should_use_rag(prompt):
                    matches = retrieve_datasheet_matches(prompt, datasheet_kb, top_k=RAG_TOP_K)

                prompt_sections: list[str] = []
                recent_history_text = build_recent_history_text(st.session_state.ui_messages[:-1], CHAT_HISTORY_TURNS)
                if recent_history_text:
                    prompt_sections.append(recent_history_text)
                prompt_sections.append(f"Tin nhắn mới nhất của bạn: {prompt}")
                private_reference_context = build_private_reference_context(matches)
                if private_reference_context:
                    prompt_sections.append(private_reference_context)

                full_prompt = "\n\n".join(prompt_sections)
                response_stream = model.generate_content(full_prompt, stream=True)

                for index, chunk in enumerate(response_stream, start=1):
                    chunk_text = getattr(chunk, "text", "")
                    if not chunk_text:
                        continue
                    full_response += chunk_text
                    if index % STREAM_UPDATE_EVERY == 0:
                        safe_stream = html.escape(sanitize_model_response(full_response)).replace("\n", "<br>")
                        message_placeholder.markdown(
                            f'<div class="chat-copy chat-copy-assistant">{safe_stream}▌</div>',
                            unsafe_allow_html=True,
                        )

                safe_response = sanitize_model_response(full_response)
                safe_final = html.escape(safe_response).replace("\n", "<br>")
                message_placeholder.markdown(
                    f'<div class="chat-copy chat-copy-assistant">{safe_final}</div>',
                    unsafe_allow_html=True,
                )
                st.session_state.ui_messages.append({"role": "assistant", "content": safe_response})
            except Exception as exc:
                st.error(f"Aura đang mệt một chút, bạn đợi lát rồi thử lại nhé! ({exc})")
