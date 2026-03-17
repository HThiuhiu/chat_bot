import streamlit as st
import google.generativeai as genai

# --- 1. CẤU HÌNH GIAO DIỆN & SIDEBAR ---
st.set_page_config(page_title="Oli Chat", page_icon="🦉", layout="centered")

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3069/3069172.png", width=100) # Thêm một icon cú dễ thương
    st.write("### Về Oli")
    st.write("Oli là người bạn AI đồng hành cảm xúc, luôn ở đây để lắng nghe và thấu hiểu bạn.")
    st.divider()
    # Nút xóa lịch sử trò chuyện
    if st.button("🗑️ Xóa lịch sử trò chuyện"):
        if "chat_session" in st.session_state:
            del st.session_state["chat_session"]
            st.rerun() # Tải lại trang để xóa UI

st.title("🦉 Oli Chat - Share with me")

# --- 2. CẤU HÌNH API AN TOÀN ---
# Sử dụng st.secrets thay vì hardcode. 
# (Xem hướng dẫn thiết lập file secrets ở bên dưới)
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except KeyError:
    st.error("🚨 Lỗi: Chưa tìm thấy API Key trong file secrets. Vui lòng kiểm tra lại cấu hình bảo mật.")
    st.stop()

# --- 3. QUẢN LÝ TRẠNG THÁI & KHỞI TẠO MODEL ---
if "chat_session" not in st.session_state:
    system_instruction = """
    Bạn là Oli, một người bạn đồng hành cảm xúc thông minh, sâu sắc và vô cùng ấm áp dành cho học sinh/sinh viên. 
    Bạn sở hữu kiến thức tâm lý học phong phú nhưng luôn diễn đạt chúng một cách gần gũi, dễ hiểu như một người bạn tri kỷ.

    Quy tắc giao tiếp cốt lõi:
    1. Thấu cảm sâu sắc: Đừng chỉ lặp lại cảm xúc của người dùng. Hãy cho thấy bạn thực sự hiểu sự phức tạp đằng sau nỗi buồn hay áp lực của họ.
    2. Phân tích nguyên nhân: Nhẹ nhàng giúp người dùng nhìn nhận lại vấn đề (ví dụ: giải thích vì sao não bộ lại phản ứng với áp lực học tập bằng sự mệt mỏi). Cung cấp góc nhìn mới mẻ để họ thoát khỏi sự bế tắc.
    3. Đề xuất giải pháp tinh tế: Không ra lệnh "bạn phải làm thế này". Hãy đưa ra một danh sách các lựa chọn/phương pháp nhỏ, dễ thực hiện (actionable steps) để họ tự chọn lựa.
    4. Trình bày thông minh: 
       - Trả lời chi tiết, mạch lạc, có chiều sâu. KHÔNG giới hạn độ dài, hãy nói cặn kẽ nếu vấn đề phức tạp.
       - Sử dụng in đậm (**text**) để nhấn mạnh các ý chính.
       - Sử dụng danh sách (bullet points) khi đưa ra các gợi ý để người dùng dễ đọc.
    5. Xưng hô: Bạn là Oli, người dùng là bạn. Kết thúc tin nhắn bằng một lời động viên hoặc một câu hỏi mở khơi gợi sự suy ngẫm sâu sắc hơn.
    """
    
    # Thêm Generation Config để tối ưu hóa câu trả lời dài và tự nhiên
    generation_config = genai.GenerationConfig(
        temperature=0.85,        # Tăng tính mềm mại, tự nhiên
        top_p=0.95, 
        max_output_tokens=1200,  # Cho phép xuất ra văn bản dài
    )

    model = genai.GenerativeModel(
        model_name='gemini-2.5-flash', 
        generation_config=generation_config,
        system_instruction=system_instruction
    )
    st.session_state.chat_session = model.start_chat(history=[])

# --- 4. HIỂN THỊ LỊCH SỬ CHAT ---
for message in st.session_state.chat_session.history:
    role = "assistant" if message.role == "model" else "user"
    with st.chat_message(role):
        st.markdown(message.parts[0].text)

# --- 5. XỬ LÝ NHẬP LIỆU & STREAMING ---
if prompt := st.chat_input("Hôm nay của bạn thế nào? Hãy kể Oli nghe nhé..."):
    # Hiển thị tin nhắn user
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Gọi AI và hiển thị hiệu ứng gõ chữ (Streaming)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Tham số stream=True giúp lấy dữ liệu về từng mảnh nhỏ
            response_stream = st.session_state.chat_session.send_message(prompt, stream=True)
            for chunk in response_stream:
                full_response += chunk.text
                # Thêm ký tự '▌' để tạo cảm giác con trỏ đang nhấp nháy
                message_placeholder.markdown(full_response + "▌")
            
            # Xóa con trỏ khi đã hoàn thành
            message_placeholder.markdown(full_response)
            
        except Exception as e:
            st.error(f"Oli đang gặp chút sự cố: {e}")