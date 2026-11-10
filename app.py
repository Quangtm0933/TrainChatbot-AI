"""
TrainChatbot — Streamlit application entry point.

Giao diện hoàn thiện: Hỗ trợ Sidebar, Quick Prompts (Câu hỏi gợi ý),
Quản lý Ngữ cảnh (Context Management) và Avatar.
"""

import streamlit as st
from services.chatbot_service import process_message

# 1. Cấu hình trang
st.set_page_config(page_title="TrainChatbot AI", page_icon="🚆", layout="wide")

# ==========================================
# GIAO DIỆN THANH BÊN (SIDEBAR)
# ==========================================
with st.sidebar:
    st.title("🚆 TrainChatbot AI")
    st.markdown("Đồ án ứng dụng **NLP, SQLite** và **Gemini**")
    st.divider()
    
    st.subheader("📍 Dữ liệu hỗ trợ Demo")
    st.markdown("""
    - **Nhà ga:** Hà Nội, Đồng Hới, Huế, Đà Nẵng, Nha Trang, Sài Gòn
    - **Ngày chạy mẫu:** `20/12/2026`
    - **Tuyến tàu:** SE1, SE3, SE5, SE7
    """)
    st.divider()

    st.subheader("💡 Câu hỏi gợi ý (Click để hỏi)")
    
    if st.button("🎫 Tìm vé Hà Nội - Huế", use_container_width=True):
        st.session_state.quick_prompt = "Tìm chuyến tàu Hà Nội đi Huế ngày 20/12/2026"
        
    if st.button("🌅 Tư vấn du lịch Đà Nẵng", use_container_width=True):
        st.session_state.quick_prompt = "Tư vấn lịch trình đi Đà Nẵng bằng tàu hỏa"
        
    if st.button("❓ Quy định đổi vé", use_container_width=True):
        st.session_state.quick_prompt = "Quy định đổi trả vé tàu thế nào?"
        
    st.divider()
    
    # Nút xóa lịch sử làm sạch toàn bộ bộ nhớ (Nút nổi bật)
    if st.button("🗑️ Xóa lịch sử trò chuyện", type="primary", use_container_width=True):
        st.session_state.chat_history = [{
            "role": "assistant", 
            "content": "Xin chào! Tôi là chatbot hỗ trợ tra cứu vé tàu. Bạn muốn đi từ ga nào đến ga nào?"
        }]
        st.session_state.booking_context = {}
        st.rerun()


# ==========================================
# GIAO DIỆN CHAT CHÍNH
# ==========================================
st.title("💬 Trợ Lý Đường Sắt Ảo")
st.caption("Hãy nhập yêu cầu của bạn hoặc chọn các câu hỏi gợi ý ở thanh bên trái.")

# Khởi tạo bộ nhớ (History & Context)
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{
        "role": "assistant", 
        "content": "Xin chào! Tôi là chatbot hỗ trợ tra cứu vé tàu. Bạn muốn đi từ ga nào đến ga nào?"
    }]
if "booking_context" not in st.session_state:
    st.session_state.booking_context = {}

# Xác định nguồn câu hỏi: Từ ô nhập text HOẶC từ nút bấm ở Sidebar
user_prompt = st.chat_input("Nhập câu hỏi của bạn (VD: Giá vé đi Đà Nẵng)...")

if "quick_prompt" in st.session_state:
    user_prompt = st.session_state.quick_prompt
    del st.session_state.quick_prompt  # Xóa sau khi đã lấy

# Hiển thị lịch sử chat kèm AVATAR
for message in st.session_state.chat_history:
    # Xác định icon dựa trên role
    avatar_icon = "👤" if message["role"] == "user" else "🚆"
    with st.chat_message(message["role"], avatar=avatar_icon):
        st.markdown(message["content"])

# Xử lý luồng chat khi có câu hỏi mới
if user_prompt:
    # 1. In câu hỏi của user
    st.session_state.chat_history.append({"role": "user", "content": user_prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_prompt)

    # 2. Xử lý và in câu trả lời của bot
    with st.chat_message("assistant", avatar="🚆"):
        with st.spinner("Đang xử lý thông tin..."):
            try:
                # Gọi service
                result = process_message(user_prompt, st.session_state.booking_context)
                
                # Cập nhật ngữ cảnh
                st.session_state.booking_context = result["context"]
                
                # Hiển thị kết quả
                bot_response = result["response"]
                st.markdown(bot_response)
                
                # Lưu vào lịch sử
                st.session_state.chat_history.append({"role": "assistant", "content": bot_response})
                
            except Exception as e:
                st.error(f"❌ Đã xảy ra lỗi hệ thống: {e}")