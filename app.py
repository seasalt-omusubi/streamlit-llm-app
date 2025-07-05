# ライブラリのインポート
import os
from dotenv import load_dotenv
import streamlit as st
from openai import OpenAI
from langchain.prompts import PromptTemplate

# Streamlitの設定（最初に配置する必要があります）
st.set_page_config(page_title="Streamlit LLM App", page_icon="🤖")

# ページタイトル
st.title("Streamlit LLM App")

# ページ説明
st.markdown("""
このアプリは、特定の専門家に質問を投げかけることができるStreamlitアプリです。
以下のラジオボタンから質問を投げたい専門家を選択してください。
選択した専門家に応じて、AIが異なる観点から回答します。
""")

# テキスト入力ボックスの作成
input_text = st.text_input("ここに質問文を入力してください:")

# ラジオボタンを追加
selected_expert = st.radio("質問を投げたい専門家LLMを選択してください", options=["小児医療専門家", "IT専門家", "法律専門家"])

# LangChainのプロンプトテンプレートを定義
expert_templates = {
    "小児医療専門家": PromptTemplate(
        input_variables=["question"],
        template="""あなたは小児医療の専門家です。
専門知識: 小児科学、小児の成長発達、小児疾患
回答スタイル: 医学的根拠に基づいた正確な情報を、保護者にも理解しやすい言葉で説明

以下の質問に専門的な観点から答えてください：
質問: {question}

回答:"""
    ),
    "IT専門家": PromptTemplate(
        input_variables=["question"],
        template="""あなたはIT技術の専門家です。
専門知識: プログラミング、システム設計、最新技術トレンド
回答スタイル: 技術的に正確で、実装可能な具体的な解決策を提示

以下の質問に技術的な観点から答えてください：
質問: {question}

回答:"""
    ),
    "法律専門家": PromptTemplate(
        input_variables=["question"],
        template="""あなたは法律の専門家です。
専門知識: 民法、商法、労働法、その他関連法規
回答スタイル: 法的根拠を明確にし、一般の方にも理解しやすい説明

以下の質問に法的な観点から答えてください：
質問: {question}

注意: これは一般的な法的情報であり、具体的な法的アドバイスについては専門家にご相談ください。

回答:"""
    )
}

# 選択された専門家に応じてプロンプトを生成
if selected_expert in expert_templates:
    prompt_template = expert_templates[selected_expert]
    expert_prompt = prompt_template.format(question=input_text) if input_text else ""

# .envファイルから環境変数を読み込む
load_dotenv()

# OpenAIのAPIキーを'.env'から取得
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

# ボタンが押下された時の処理
if st.button("AIに質問する"):
    if not input_text:
        st.error("質問文を入力してください")
    else:
        try:
            with st.spinner("AIが回答中..."):
                # ストリーミング出力用のコンテナを作成
                response_container = st.empty()
                full_response = ""
                
                # 生成されたプロンプトを表示（デバッグ用）
                with st.expander("使用されたプロンプト（クリックして表示）"):
                    st.text(expert_prompt)
                
                # ストリーミングAPIの使用
                stream = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "user", "content": expert_prompt}
                    ],
                    stream=True  # ストリーミングを有効化
                )
                
                # ストリーミングレスポンスを処理
                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        full_response += chunk.choices[0].delta.content
                        # リアルタイムで応答を更新
                        response_container.markdown(f"**AIの回答：**\n\n{full_response}")
                
                st.success("AIの回答が完了しました")
                
        except Exception as e:
            st.error(f"エラーが発生しました: {str(e)}")