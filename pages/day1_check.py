import streamlit as st
import json
import os
from datetime import datetime
from typing import TypedDict, List, Optional, Dict
from enum import Enum


# 質問タイプの定義
class QuestionType(Enum):
    TEXT_INPUT = "text_input"
    TEXT_AREA = "text_area"
    RADIO = "radio"
    MULTISELECT = "multiselect"


# 質問一覧の型定義
class Question(TypedDict):
    name: str
    type: QuestionType
    label: str
    options: Optional[List[str]]  # selectbox や radiobutton で使用
    required: bool  # 必須回答かどうか


# 保存先 JSON ファイルパス
FILE_PATH = "responses.json"

# 質問一覧の定義
questions: List[Question] = [
    {
        "name": "email",
        "type": QuestionType.TEXT_INPUT,
        "label": "メールアドレス",
        "options": None,
        "required": True,
    },
    {
        "name": "name",
        "type": QuestionType.TEXT_INPUT,
        "label": "氏名",
        "options": None,
        "required": True,
    },
    {
        "name": "api_key_role",
        "type": QuestionType.RADIO,
        "label": ".envファイルにOpenAIのAPIキーを記載しましたが、このAPIキーの役割として正しいものを1つ選択してください。",
        "options": [
            "A. APIを使ったアプリケーションを「誰が使っているのか？」を識別するための文字列です。これによってLLMなどのサービス提供側は利用者を識別し、不正利用の防止や課金の管理を行います。",
            "B. APIのやり取りするデータを暗号化するためのパスワードです。これによって、通信途中のデータが他人に見られてしまうのを防ぎます。",
            "C. 複数のサービスのAPIを使う場合に、どのAPIを使うのかを識別するための文字列です。これによって、目的のAPIを正しく呼び出せるようにしています。",
        ],
        "required": True,
    },
    {
        "name": "token_explanation",
        "type": QuestionType.RADIO,
        "label": "LLMにおけるトークンの説明として正しいものを1つ選択してください。",
        "options": [
            "A. LLMのサービスにアクセスする際に使う認証用の文字列のことです。",
            "B. LLMがテキストを理解・生成する際に扱う文字列の単位のことです。",
            "C. LLMの利用量に応じた費用の決済に用いることができる仮想通貨のことです。",
        ],
        "required": True,
    },
    {
        "name": "json_mode",
        "type": QuestionType.RADIO,
        "label": "JSONモードの説明として正しいものを1つ選択してください。",
        "options": [
            "A. LLMへの入力を、JSON形式で行うように指定する機能です。",
            "B. LLMからの出力を、JSON形式で行うように指定する機能です。",
            "C. LLMの入力と出力を、JSON形式で行うように指定する機能です。",
        ],
        "required": True,
    },
    {
        "name": "function_calling",
        "type": QuestionType.RADIO,
        "label": "Function callingの説明として正しいものを1つ選択してください。",
        "options": [
            "A. LLMに関数を実行させる機能です。アプリケーション側で事前に用意した関数を、LLMが必要と判断した時に直接実行します。",
            "B. LLMに関数の実行が必要かどうかを判断させる機能です。事前に用意した関数の仕様を伝えると、LLMが必要と判断した時にその旨を返します。ただし、LLMは判断するだけであり関数を直接実行することはありません。",
            "C. LLMに要件を伝えて、実行が必要な関数の中身を考案させる機能です。ただし、LLMは考案するだけであり実際の関数を実装することはありません。",
        ],
        "required": True,
    },
    {
        "name": "prompt_engineering",
        "type": QuestionType.RADIO,
        "label": "プロンプトエンジニアリングの説明として正しいものを1つ選択してください。",
        "options": [
            "A. LLMから望む回答を得るために、LLMの出力テキストを解析する技術のことです。",
            "B. LLMから望む回答を得るために、LLMアプリケーションのUIをデザインしたり工夫したりする作業のことです。",
            "C. LLMから望む回答を得るために、プロンプトを設計・調整する技術やプロセスのことです。",
        ],
        "required": True,
    },
    {
        "name": "reasoning_model",
        "type": QuestionType.RADIO,
        "label": "OpenAIのReasoningモデル（oシリーズ）の特徴として正しいものを1つ選択してください。",
        "options": [
            "A. Reasoningモデル（oシリーズ）は、GPTシリーズよりも数学の問題解決能力が高いです。",
            "B. Reasoningモデル（oシリーズ）は、GPTシリーズよりも高速に応答を得ることができます。",
            "C. Reasoningモデル（oシリーズ）を使うために、Chat Completions APIではない専用のAPIが提供されています。",
        ],
        "required": True,
    },
    {
        "name": "langchain_explanation",
        "type": QuestionType.MULTISELECT,
        "label": "LangChainについての説明で正しいものを「すべて」選択してください。",
        "options": [
            "A. LangChainはLLMアプリケーションを開発しやすくするためのフレームワークです。幅広い分野をカバーしており、さまざまな種類のアプリケーション開発に利用できます。",
            "B. LangChainを使えば、さまざまなLLMを共通のインターフェースで利用できます。LLMごとのAPI仕様の差を吸収するラッパーの機能を持つと言えます。",
            "C. LangChainは、公式ドキュメントやクックブックに論文などで提案された手法の実装例が多数掲載されており、LLMアプリケーションの開発を学ぶために大変適しています。ただし、破壊的変更が多いためにプロダクショングレードでの利用は推奨されておらず、実運用の事例もまだありません。",
        ],
        "required": True,
    },
    {
        "name": "rag_explanation",
        "type": QuestionType.RADIO,
        "label": "RAG（Retrieval-Augmented Generation：検索拡張生成）の説明として正しいものを1つ選択してください。",
        "options": [
            "A. RAGとは検索機能をLLMによって拡張する仕組みです。従来の検索機能では新しい情報や企業内の秘密情報は検索できませんでしたが、LLMと組み合わせることでそれを可能にします。",
            "B. RAGとはLLMを検索機能によって拡張する仕組みです。LLMでは新しい情報や企業内の秘密情報に基づく回答ができませんでしたが、検索機能と組み合わせることでそれを可能にします。",
            "C. RAGとはChromaなどで使われている検索技術のことです。LLMとは関係しない技術でしたが、LLMとの組み合わせが有効なことがわかり昨今注目されています。",
        ],
        "required": True,
    },
    {
        "name": "framework_matching",
        "type": QuestionType.RADIO,
        "label": "「(a)はLLMアプリケーションを開発するためのフレームワークです。(b)はLLMアプリケーションのトレースや評価などを支援してくれるWebサービスです。(c)はPythonでUIを簡易的につくるためのパッケージです。」",
        "options": [
            "A. (a)LangChain (b)Streamlit (c)LangSmith",
            "B. (a)LangChain (b)Chroma (c)LangSmith",
            "C. (a)LangChain (b)LangSmith (c)Streamlit",
        ],
        "required": True,
    },
    {
        "name": "chroma_indexing",
        "type": QuestionType.RADIO,
        "label": "RAGアプリケーションのハンズオンでChromaによるインデクシングの処理を実装しましたが、その処理について正しいものを1つ選択してください。",
        "options": [
            "A. Chromaにおけるインデクシングとは、事前に検索対象の文書を暗号化して、セキュアに検索できるように格納する作業のことです。",
            "B. Chromaにおけるインデクシングとは、事前に検索対象の文書をベクトル化して、ベクトルによる検索ができるように格納する作業のことです。",
            "C. Chromaにおけるインデクシングとは、事前に検索対象の文書を単語で分割して、単語を理解した検索ができるように格納する作業のことです。",
        ],
        "required": True,
    },
    {
        "name": "business_application",
        "type": QuestionType.TEXT_AREA,
        "label": "もし、業務活用を考えているLLMアプリケーションの構想がありましたら、差し支えない範囲で概要を教えてください。また、まだ構想がない場合は、身の回りの業務に活用できそうなLLMアプリケーションのアイデアを1つ考えてみてください。",
        "options": None,
        "required": True,
    },
]


def app() -> None:
    """
    Streamlit アプリのメイン処理
    """
    st.title("理解度テスト")

    # レスポンス格納用
    responses: Dict[str, str] = {}

    with st.form("survey_form"):
        for q in questions:
            qtype = q["type"]
            key = q["name"]
            label = q["label"]
            required = q["required"]

            # 必須項目の場合はラベルに * を追加
            display_label = f"{label} *" if required else label

            if qtype == QuestionType.TEXT_INPUT:
                responses[key] = st.text_input(display_label, key=key)
            elif qtype == QuestionType.TEXT_AREA:
                responses[key] = st.text_area(display_label, key=key)
            elif qtype == QuestionType.RADIO:
                opts = q.get("options") or []
                responses[key] = st.radio(display_label, opts, key=key)
            elif qtype == QuestionType.MULTISELECT:
                opts = q.get("options") or []
                selected = st.multiselect(display_label, opts, key=key)
                responses[key] = ", ".join(selected)
            else:
                st.warning(f"未対応の質問タイプ: {qtype}")

        submitted = st.form_submit_button("送信")

    if submitted:
        # 必須項目のバリデーション
        missing_required = []
        for q in questions:
            if q["required"] and not responses.get(q["name"], "").strip():
                missing_required.append(q["label"])

        if missing_required:
            st.error(f"以下の必須項目が未入力です: {', '.join(missing_required)}")
            return

        # タイムスタンプを追加
        responses["timestamp"] = datetime.now().isoformat()

        # 既存のデータ読み込み
        existing_data: List[Dict[str, str]] = []
        if os.path.exists(FILE_PATH):
            with open(FILE_PATH, "r", encoding="utf-8") as f:
                existing_data = json.load(f)

        # 新しい回答を追加
        existing_data.append(responses)

        # ファイルへ書き込み
        with open(FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)

        # 結果表示
        st.success("ご回答ありがとうございました！")
        st.json(responses)


app()
