# LMY Chatbot (Streamlit + Gemini) - Oli-like Emotional Companion

App này là một chatbot trên **Streamlit**. Bot có tên **LMY** và có thể tham khảo dữ liệu từ file **`datasheet.xlsx`** để hỗ trợ trả lời (dạng RAG: tìm ví dụ phù hợp rồi đưa vào prompt).

## Tính năng chính

- Giao diện chat dạng Streamlit (`st.chat_input`, hiển thị lịch sử hội thoại).
- Tải dữ liệu từ `datasheet.xlsx` (sheet `Tổng hợp`) để tìm các dòng diễn ngôn/ cảm xúc gần với câu người dùng.
- Dùng dữ liệu tìm được làm **tham khảo nội bộ** (không trích nguyên văn cho người dùng).
- Tách UI (HTML/CSS) vào thư mục `ui/` và logic vào `src/` để dễ bảo trì.

## Yêu cầu

- macOS / Linux / Windows đều được (Streamlit + Python).
- Python 3.10+ (project đang dùng Python 3.13 trong môi trường hiện tại).
- Tài khoản Google Gemini API và **API key**.

## Cài đặt (Local)

### 1) Tạo môi trường và cài dependency

```bash
cd "/Users/thisistuns/Downloads/chatAI/chat_bot"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Cấu hình Gemini API Key

App đọc key từ file:

`./.streamlit/secrets.toml`

Tạo thư mục và file:

```bash
mkdir -p .streamlit
```

`./.streamlit/secrets.toml`

```toml
GEMINI_API_KEY = "YOUR_API_KEY_HERE"
APP_URL = "https://your-app-name.streamlit.app/"
```

> Không commit file `.streamlit/secrets.toml` lên Git nếu có chứa key thật.

### 3) Chạy app

```bash
streamlit run app.py
```

Mở trình duyệt:

- `http://localhost:8501` (port mặc định của Streamlit)

## Cấu trúc thư mục

```text
chat_bot/
  app.py                     # Entry point Streamlit
  requirements.txt
  datasheet.xlsx             # File Excel để tham khảo (đặt trong cùng thư mục)

  ui/                        # Tách UI HTML/CSS
    styles.css
    hero.html
    education_line.html
    box1.html
    box2.html
    box3.html
    box4.html

  src/                       # Tách logic
    datasheet_rag.py         # Đọc datasheet + truy xuất ví dụ liên quan
    prompts.py              # System prompt cho LMY
    __init__.py
```

## Cách hoạt động của phần “học dữ liệu” từ `datasheet.xlsx`

- Khi bạn gửi câu chat, app:
  1. Đọc `datasheet.xlsx` (sheet `Tổng hợp`).
  2. Tạo một list các mẫu kiến thức dạng dict, mỗi mẫu có các trường:
     - `diễn_ngôn`, `cảm_xúc`, `phán_xét`, `thẩm_giá` (tìm theo tên cột)
  3. Tính điểm tương đồng thô dựa trên token overlap + `SequenceMatcher`.
  4. Lấy `top_k` dòng phù hợp nhất và đưa vào prompt dưới dạng **nội dung tham khảo nội bộ**.

> Mục tiêu: Bot có “gợi ý theo ví dụ” từ datasheet để trả lời đúng phong cách/đúng ngữ cảnh, nhưng không nên hiển thị nguyên văn các dòng đó cho người dùng.

## Gợi ý sử dụng

- Nếu bạn bật tham khảo datasheet, hãy hỏi theo kiểu “Mình đang…” / “Em cảm thấy…” để bot nhận diện cảm xúc tốt hơn.
- Nếu gặp lỗi quota (hết hạn mức), tắt tham khảo datasheet hoặc đợi quota reset.

## Troubleshooting

### Lỗi thiếu `openpyxl`

Nếu bạn gặp lỗi khi đọc `.xlsx`, cài lại dependency:

```bash
pip install -r requirements.txt
```

`openpyxl` đã được thêm vào requirements trong dự án này.

### Lỗi Gemini vượt quota / rate limit

- Khi quota hết hạn mức, Gemini sẽ trả lỗi 429/quota.
- Cách xử lý:
  1. Đợi một thời gian để quota reset
  2. Hoặc đổi sang API key có billing tốt hơn
  3. Trong sidebar, tắt “Dùng datasheet.xlsx để tham khảo” để giảm token sử dụng.

## Ghi chú

- Thư viện `google-generativeai` có trạng thái deprecated. Nếu bạn muốn cập nhật sang `google.genai`, mình có thể hỗ trợ thay code theo API mới.
- Hiện tại app chỉ “tra cứu theo file” (RAG), không huấn luyện lại model.
