# # app.py

# import streamlit as st
# from src.rag_pipeline import ChatbotPipeline
# import nest_asyncio  # <-- Thêm dòng này

# nest_asyncio.apply() # <-- Và thêm dòng này
# # --- Cấu hình trang ---
# st.set_page_config(
#     page_title="Trợ lý AI của Anh Khoa",
#     page_icon="🤖"
# )

# # --- State Management ---
# # Khởi tạo chatbot pipeline và lưu vào session state để không phải load lại
# # Dùng st.cache_resource để cache lại resource này
# @st.cache_resource
# def load_chatbot_pipeline():
#     return ChatbotPipeline()

# chatbot = load_chatbot_pipeline()

# # Khởi tạo lịch sử chat
# if "messages" not in st.session_state:
#     st.session_state.messages = [{"role": "assistant", "content": "Xin chào! Tôi có thể giúp bạn tìm hiểu gì về Anh Khoa?"}]

# # --- Giao diện ---
# st.title("🤖 Chatbot Portfolio của Anh Khoa")
# st.caption("Đây là một trợ lý AI được xây dựng bằng RAG, có thể trả lời các câu hỏi về kinh nghiệm, kỹ năng và dự án của tôi.")

# # Hiển thị các tin nhắn đã có
# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])

# # Xử lý input từ người dùng
# if prompt := st.chat_input("Hãy hỏi tôi về các dự án đã làm..."):
#     # Thêm tin nhắn của người dùng vào lịch sử
#     st.session_state.messages.append({"role": "user", "content": prompt})
#     # Hiển thị tin nhắn của người dùng
#     with st.chat_message("user"):
#         st.markdown(prompt)

#     # Hiển thị tin nhắn của trợ lý
#     with st.chat_message("assistant"):
#         # Hiển thị spinner trong khi chờ phản hồi
#         with st.spinner("Đang suy nghĩ..."):
#             response = chatbot.get_response(prompt)
#             st.markdown(response)

#     # Thêm tin nhắn của trợ lý vào lịch sử
#     st.session_state.messages.append({"role": "assistant", "content": response})


# app_pretty.py
# A prettier Streamlit UI wrapper for your RAG chatbot

# __import__('pysqlite3')
# import sys
# sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st
from datetime import datetime
from typing import List, Dict
# import nest_asyncio

# RAG pipeline
from src.rag_pipeline import ChatbotPipeline

# ---- Patch nested event loops (Jupyter/Streamlit) ----
# nest_asyncio.apply()
import time
import random


# -------------------- SPAM/CAPTCHA Logic --------------------
def initialize_spam_protection():
    """Khởi tạo các biến cần thiết trong session state."""
    if 'require_captcha' not in st.session_state:
        st.session_state.require_captcha = False
    if 'request_timestamps' not in st.session_state:
        st.session_state.request_timestamps = []

def check_rate_limit(max_requests: int, per_seconds: int) -> bool:
    """Kiểm tra rate limit. Nếu vi phạm, kích hoạt CAPTCHA."""
    current_time = time.time()
    st.session_state.request_timestamps = [
        ts for ts in st.session_state.request_timestamps
        if current_time - ts < per_seconds
    ]

    if len(st.session_state.request_timestamps) >= max_requests:
        st.session_state.require_captcha = True # Kích hoạt CAPTCHA
        return False

    st.session_state.request_timestamps.append(current_time)
    return True

def generate_captcha():
    """Tạo câu hỏi toán học mới."""
    st.session_state.num1 = random.randint(1, 10)
    st.session_state.num2 = random.randint(1, 10)
    st.session_state.captcha_answer = st.session_state.num1 + st.session_state.num2

def captcha_check():
    """Kiểm tra câu trả lời và tắt CAPTCHA nếu đúng."""
    user_answer = st.session_state.get('captcha_input', '')
    if user_answer.isdigit() and int(user_answer) == st.session_state.captcha_answer:
        st.session_state.require_captcha = False # Tắt CAPTCHA
        st.success("Xác minh thành công! Bạn có thể tiếp tục trò chuyện.")
        # Xóa các biến không cần thiết
        del st.session_state.num1
        del st.session_state.num2
        del st.session_state.captcha_answer
        time.sleep(2) # Chờ 2 giây để người dùng đọc thông báo
        st.rerun()
    else:
        st.error("Câu trả lời không đúng. Vui lòng thử lại.")
        generate_captcha() # Tạo câu hỏi mới

# -------------------- Page Config --------------------
st.set_page_config(
    page_title="Trợ lý AI của Anh Khoa",
    page_icon="🤖",
    layout="wide"
)

# -------------------- Custom CSS ---------------------
CUSTOM_CSS = """
<style>
/* widen content and tweak fonts */
.main .block-container {max-width: 1100px; padding-top: 1.2rem;}
/* hero section */
.hero {
  padding: 1.25rem 1.25rem;
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(33,150,243,0.08), rgba(250,130,28,0.08));
  border: 1px solid rgba(127,127,127,0.15);
  margin-bottom: 1rem;
}
.hero h1 {
  font-size: 2rem;
  margin: 0 0 .25rem 0;
}
.hero p {
  margin: 0;
  opacity: .85;
}

/* chat bubbles */
.stChatMessage[data-testid="stChatMessage"] {
  border-radius: 14px;
  padding: .6rem .75rem;
  margin-bottom: .5rem;
  border: 1px solid rgba(127,127,127,0.15);
}
.stChatMessage[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p {
  margin-bottom: .6rem;
}
/* assistant bubble tint */
.stChatMessage:nth-child(odd) {
  background: rgba(33,150,243,0.05);
}
/* user bubble tint */
.stChatMessage:nth-child(even) {
  background: rgba(250,130,28,0.06);
}

/* chip buttons */
.chips button[kind="secondary"] {
  border-radius: 999px !important;
  padding: .25rem .75rem !important;
  margin-right: .35rem !important;
  margin-bottom: .35rem !important;
}

/* small caption row */
.meta-row {
  font-size: .85rem;
  opacity: .8;
}

/* sidebar card */
.sidebar-card {
  padding: .75rem;
  border-radius: 14px;
  border: 1px solid rgba(127,127,127,0.15);
  background: rgba(0,0,0,0.02);
}
.sidebar-card h4 {
  margin-top: 0;
  margin-bottom: .5rem;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -------------------- Helpers --------------------
def ensure_session():
    if "messages" not in st.session_state:
        st.session_state.messages: List[Dict[str, str]] = [
            {"role": "assistant", "content": "Xin chào! Tôi có thể giúp bạn tìm hiểu gì về Anh Khoa?"}
        ]
    if "suggestions" not in st.session_state:
        st.session_state.suggestions = [
            "Show my projects using Next.js",
            "What did I do at Cyno Software?",
            "List my experience timeline",
            "Which projects use PostgreSQL?",
            "Give a short bio based on my CV"
        ]

def append_message(role: str, content: str):
    st.session_state.messages.append({"role": role, "content": content})

def run_query(chatbot: "ChatbotPipeline", user_text: str) -> str:
    # Keep the app resilient if your pipeline raises.
    try:
        return chatbot.get_response(user_text)
    except Exception as e:
        return f"❌ Error from pipeline: `{e}`"

# -------------------- Cache RAG pipeline --------------------
@st.cache_resource
def load_chatbot_pipeline():
    return ChatbotPipeline()

chatbot = load_chatbot_pipeline()
ensure_session()
initialize_spam_protection()
# -------------------- Sidebar --------------------
with st.sidebar:
    st.image("https://kflower.me/images/avatar.png", caption="Nguyen Anh Khoa", use_container_width=True)
    st.markdown("""
<div class="sidebar-card">
<h4>About</h4>
<b>Role:</b> Full-Stack / Front-End developer<br/>
<b>Focus:</b> Next.js, React, Node.js, PostgreSQL<br/>
<b>Location:</b> Ho Chi Minh City, Vietnam
</div>
""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### Quick actions")
    col1, col2 = st.columns(2)
    if col1.button("🧹 New chat"):
        st.session_state.messages = [{"role": "assistant", "content": "Bắt đầu cuộc trò chuyện mới. Bạn muốn hỏi gì về hồ sơ của tôi?"}]
        st.rerun()
    st.download_button(
        "⬇️ Export chat",
        data="\n\n".join([f"**{m['role']}**: {m['content']}" for m in st.session_state.messages]).encode("utf-8"),
        file_name=f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
        mime="text/markdown"
    )

    st.markdown("---")
    st.markdown("#### Links")
    st.link_button("🌐 Portfolio", "https://akflower.vercel.app")
    st.link_button("💼 LinkedIn", "https://www.linkedin.com/in/akflower")
    st.link_button("📂 GitHub", "https://github.com/AKflower")

# -------------------- Header / Hero --------------------
st.markdown("""
<div class="hero">
  <h1>🤖 Chatbot Portfolio — Nguyen Anh Khoa</h1>
  <p>This assistant uses a RAG pipeline to answer questions about my experiences, skills, and projects.</p>
</div>
""", unsafe_allow_html=True)

# -------------------- Suggestion Chips --------------------
with st.container():
    st.caption("Try one of these:")
    cols = st.columns(5)
    for i, sug in enumerate(st.session_state.suggestions[:5]):
        if cols[i].button(sug, key=f"sug_{i}", type="secondary"):
            # Simulate user message from chip
            append_message("user", sug)
            with st.chat_message("user", avatar="🧑‍💻"):
                st.markdown(sug)

            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner("Thinking..."):
                    resp = run_query(chatbot, sug)
                    st.markdown(resp)
            append_message("assistant", resp)
            st.stop()

# -------------------- Chat History --------------------
for message in st.session_state.messages:
    avatar = "🤖" if message["role"] == "assistant" else "🧑‍💻"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])



if st.session_state.require_captcha:
    st.warning("Bạn đã gửi yêu cầu quá nhanh. Vui lòng xác minh bạn là người thật để tiếp tục.")

    if 'num1' not in st.session_state:
        generate_captcha()

    st.write(f"Vui lòng trả lời câu hỏi sau: **{st.session_state.num1} + {st.session_state.num2} = ?**")

    st.text_input(
        "Nhập câu trả lời và nhấn Enter:",
        key="captcha_input",
        on_change=captcha_check
    )

# -------------------- Chat Input --------------------
prompt_disabled = st.session_state.require_captcha

if prompt := st.chat_input("Ask me about my work, skills, or projects..."):
    if check_rate_limit(max_requests=5, per_seconds=30):
        append_message("user", prompt)
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Thinking..."):
                response = run_query(chatbot, prompt)
                st.markdown(response)

        append_message("assistant", response)
        st.rerun() # Chạy lại để xóa input sau khi gửi
    else:
        st.rerun() # Chạy lại để hiển thị CAPTCHA


# -------------------- Footer --------------------
st.markdown(
    '<div class="meta-row">Made with ❤️ using Streamlit · Last updated: '
    + datetime.now().strftime("%Y-%m-%d %H:%M")
    + "</div>",
    unsafe_allow_html=True,
)
