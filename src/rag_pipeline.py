# src/rag_pipeline.py

import os
from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Tải biến môi trường
load_dotenv()

# Định nghĩa đường dẫn tới vector store
VECTOR_STORE_PATH = "vector_store/"

class ChatbotPipeline:
    def __init__(self):
        # 1. Khởi tạo LLM
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.3,
            convert_system_message_to_human=True
        )

        # 2. Prompt Template
        self.prompt = ChatPromptTemplate.from_template(
            """
            Bạn là một trợ lý AI đại diện cho Anh Khoa.
            Nhiệm vụ của bạn là trả lời các câu hỏi về kinh nghiệm, kỹ năng và dự án của Anh Khoa chỉ dựa trên nội dung được cung cấp dưới đây.

            **Nội dung:**
            {context}

            **Câu hỏi:**
            {question}

            **Quy tắc:**
            - Giọng văn chuyên nghiệp, thân thiện.
            - Pha một chút hài hước nếu hỏi về tình cảm, nhan sắc hoặc tài chính.
            - Trả lời ở ngôi thứ ba.
            - Nếu không biết, hãy lịch sự trả lời và gợi ý liên hệ email: anhkhoabqv@gmail.com.
            - Tuyệt đối **KHÔNG** bịa đặt thông tin.

            **Câu trả lời của bạn:**
            """
        )

        # 3. Vector Store & Retriever
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        vector_store = Chroma(
            persist_directory=VECTOR_STORE_PATH,
            embedding_function=embeddings
        )
        self.retriever = vector_store.as_retriever(search_kwargs={"k": 10})

        # 4. RAG Chain
        self.chain = (
            {"context": self.retriever, "question": RunnablePassthrough()}
            | self.prompt
            | self.llm
            | StrOutputParser()
        )

    def get_response(self, query):
        return self.chain.invoke(query)


if __name__ == '__main__':
    chatbot = ChatbotPipeline()
    print(chatbot.get_response("Anh Khoa có những dự án nào nổi bật?"))
