import streamlit as st
import google.generativeai as genai

# --- 1. CẤU HÌNH TRANG VÀ CSS TÙY CHỈNH ---
st.set_page_config(page_title="Ra mắt Oli - Chatbot AI", page_icon="🦉", layout="wide")

# Nhúng mã CSS để tạo các hộp màu, font chữ và bố cục
st.markdown("""
    <style>
    /* Reset & General Setup */
    .stApp { background-color: #fdfbf7; } /* Màu nền hơi kem nhẹ */
    
    .info-box {
        border-radius: 25px;
        padding: 25px 30px;
        margin-bottom: 30px;
        color: #333;
        font-size: 15px;
        line-height: 1.6;
        box-shadow: 2px 4px 15px rgba(0,0,0,0.04);
    }
    
    /* Màu sắc các hộp dựa theo ảnh */
    .box1 { background-color: #dfd8cd; } 
    .box2 { background-color: #adddf5; } 
    .box3 { background-color: #ecd2df; } 
    .box4 { background-color: #ebe7dd; } 
    
    .circle-num {
        display: inline-flex;
        width: 36px;
        height: 36px;
        background-color: #333;
        color: white;
        border-radius: 50%;
        align-items: center;
        justify-content: center;
        font-weight: 900;
        font-size: 18px;
        margin-right: 12px;
        flex-shrink: 0;
    }
    
    .box-title {
        font-size: 20px;
        font-weight: 900;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        color: #333;
    }
    
    /* Dành riêng cho hộp số 2 có số nằm bên phải */
    .box-title-right {
        justify-content: space-between;
    }
    
    .info-box ul { padding-left: 20px; margin-top: 5px; }
    .info-box li { margin-bottom: 12px; }
    
    /* Thiết kế riêng cho Header/Hero section */
    .hero-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 30px;
        margin-top: 20px;
        margin-bottom: 50px;
    }
    .hero-text-block {
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    .hero-title {
        font-size: 85px;
        font-weight: 900;
        line-height: 1;
        font-family: 'Arial Black', Impact, sans-serif;
        display: flex;
        gap: 15px;
    }
    .hero-oli { color: #325b75; }
    .hero-chat { color: #d8a085; }
    .hero-subtitle {
        background-color: #f1b2a1;
        color: white;
        font-size: 32px;
        font-weight: bold;
        padding: 10px 50px;
        border-radius: 40px;
        margin-top: 10px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. GIAO DIỆN GIỚI THIỆU (INFOGRAPHIC) ---
st.markdown("<div style='text-align: right; color: #666; font-size: 14px;'><strong>Giáo dục</strong> | Ra mắt Oli – Chatbot AI hỗ trợ nhận diện cảm xúc học sinh...</div><hr style='margin-top: 5px;'>", unsafe_allow_html=True)

# Phần Tiêu đề chính (Hero Section) sử dụng HTML Flexbox để giống layout nhất
hero_html = """
<div class="hero-container">
    <img src="https://cdn-icons-png.flaticon.com/512/3069/3069172.png" width="180" style="object-fit: contain;">
    <div class="hero-text-block">
        <div class="hero-title">
            <span class="hero-oli">OLI</span>
            <span class="hero-chat">CHAT</span>
        </div>
        <div class="hero-subtitle">Share with me</div>
    </div>
</div>
"""
st.markdown(hero_html, unsafe_allow_html=True)

# Phần Chia cột cho 4 hộp thông tin (Dùng gap="large" để tạo độ thoáng)
col1, col2 = st.columns(2, gap="large")

with col1:
    # Hộp 1
    st.markdown("""
    <div class="info-box box1">
        <div class="box-title"><span class="circle-num">1</span> Khi nào bạn nên sử dụng Oli?</div>
        <ul>
            <li>Bất cứ lúc nào bạn cảm thấy buồn bực, lo lắng, căng thẳng hay bối rối vì chuyện học hành, bạn bè, gia đình...</li>
            <li>Khi muốn có một "người bạn" tâm sự, lắng nghe mà không sợ bị đánh giá hay xin lời khuyên ngay lập tức.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Hộp 3
    st.markdown("""
    <div class="info-box box3">
        <div class="box-title"><span class="circle-num">3</span> Tùy chỉnh Oli theo yêu cầu</div>
        <ul>
            <li>Nếu bạn chỉ muốn được lắng nghe? Hãy nhắn "Mình chỉ muốn được lắng nghe thôi."<br><i>→ Oli sẽ tạm dừng việc đặt câu hỏi, chỉ ở bên để lắng nghe bạn.</i></li>
            <li>Nếu bạn muốn đổi cách xưng hô? Ví dụ: "Gọi mình là X nhé" hoặc "Oli gọi mình là em cũng được."<br><i>→ Oli sẽ dùng cách xưng hô bạn cảm thấy thoải mái nhất.</i></li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    # Hộp 2 (Số 2 nằm bên phải)
    st.markdown("""
    <div class="info-box box2">
        <div class="box-title box-title-right">
            <span>Oli hỗ trợ bạn<br>như thế nào?</span> 
            <span class="circle-num" style="margin-right:0;">2</span>
        </div>
        <ul>
            <li>Oli không đưa lời khuyên sẵn có, mà luôn đặt câu hỏi gợi mở để bạn tự nhận diện rõ cảm xúc và nguyên nhân sâu xa của vấn đề.</li>
            <li>Oli sẽ hướng dẫn bạn cách tự suy nghĩ, nhận diện vấn đề, từ đó bạn sẽ tự tìm ra giải pháp phù hợp với mình, thay vì chỉ bảo bạn "phải làm thế này này".</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Mã QR tự động tạo hình ảnh dựa trên Link Streamlit của bạn
    app_url = "https://chatbot-zuckxrzzsttqfgqedvwat3.streamlit.app/"
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=160x160&data={app_url}"
    st.markdown(f"<div style='text-align: center; margin: 10px 0 30px 0;'><img src='{qr_url}' style='border-radius:15px; border: 5px solid #333;'></div>", unsafe_allow_html=True)
    
    # Hộp 4
    st.markdown("""
    <div class="info-box box4">
        <div class="box-title"><span class="circle-num">4</span> Hãy chia sẻ cảm xúc thật của mình</div>
        <ul>
            <li>Nói ra những lời thật lòng sẽ giúp Oli hiểu đúng, hỗ trợ đúng và đồng cảm tốt hơn.</li>
            <li>Đừng ngại bày tỏ cảm xúc của mình để Oli cùng bạn giải tỏa và xử lý vấn đề bạn nhé.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# --- 3. KHỞI TẠO LOGIC AI ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except KeyError:
    st.error("🚨 Lỗi: Chưa cấu hình API Key trong file secrets.toml")
    st.stop()

if "chat_session" not in st.session_state:
    system_instruction = """
    Bạn là Oli, một người bạn đồng hành cảm xúc thông minh, sâu sắc và vô cùng ấm áp dành cho học sinh/sinh viên. 
    Quy tắc giao tiếp cốt lõi:
    1. Thấu cảm sâu sắc: Đừng chỉ lặp lại cảm xúc của người dùng. Hãy cho thấy bạn thực sự hiểu sự phức tạp đằng sau nỗi buồn hay áp lực của họ.
    2. Phân tích nguyên nhân: Nhẹ nhàng giúp người dùng nhìn nhận lại vấn đề. Cung cấp góc nhìn mới mẻ để họ thoát khỏi sự bế tắc.
    3. Đề xuất giải pháp tinh tế: Đưa ra lựa chọn, không ra lệnh.
    4. Xưng hô: Bạn là Oli, người dùng là bạn. Kết thúc tin nhắn bằng lời động viên hoặc câu hỏi mở.
    """
    generation_config = genai.GenerationConfig(temperature=0.85, top_p=0.95, max_output_tokens=2500)
    model = genai.GenerativeModel(model_name='gemini-2.5-flash', generation_config=generation_config, system_instruction=system_instruction)
    st.session_state.chat_session = model.start_chat(history=[])

# --- 4. GIAO DIỆN KHUNG CHAT ---
st.markdown("### 💬 Bắt đầu trò chuyện với Oli tại đây 👇")

if st.button("🗑️ Xóa cuộc trò chuyện để bắt đầu lại"):
    del st.session_state["chat_session"]
    st.rerun()

chat_container = st.container(height=500)
with chat_container:
    for message in st.session_state.chat_session.history:
        role = "assistant" if message.role == "model" else "user"
        with st.chat_message(role):
            st.markdown(message.parts[0].text)

if prompt := st.chat_input("Hôm nay của bạn thế nào? Hãy kể Oli nghe nhé..."):
    with chat_container:
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            try:
                response_stream = st.session_state.chat_session.send_message(prompt, stream=True)
                for chunk in response_stream:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
            except Exception as e:
                st.error("Oli đang mệt một chút, bạn đợi lát rồi thử lại nhé!")
