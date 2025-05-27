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
    SELECTBOX = "selectbox"


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
        "name": "satisfaction",
        "type": QuestionType.RADIO,
        "label": "満足度を5段階から選んでください",
        "options": [
            "5 - 非常に満足",
            "4 - 満足",
            "3 - 普通",
            "2 - やや不満",
            "1 - 不満",
        ],
        "required": True,
    },
    {
        "name": "satisfaction_reason",
        "type": QuestionType.TEXT_AREA,
        "label": "上記の満足度を選んだ理由を教えてください",
        "options": None,
        "required": True,
    },
    {
        "name": "helpful_points",
        "type": QuestionType.TEXT_AREA,
        "label": "参考になった点や、印象的だった点があれば教えてください",
        "options": None,
        "required": False,
    },
    {
        "name": "unclear_points",
        "type": QuestionType.TEXT_AREA,
        "label": "わかりにくかった点や、講師に聞きたい点があれば教えてください",
        "options": None,
        "required": False,
    },
    {
        "name": "future_topics",
        "type": QuestionType.TEXT_AREA,
        "label": "今回のような講座として、今後受講したいテーマがあれば自由にご記入ください",
        "options": None,
        "required": False,
    },
    {
        "name": "other_comments",
        "type": QuestionType.TEXT_AREA,
        "label": "その他、お気付きの点やコメントなどあれば気軽にご記入ください",
        "options": None,
        "required": False,
    },
]


def app() -> None:
    """
    Streamlit アプリのメイン処理
    """
    st.title("アンケート")

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
            elif qtype == QuestionType.SELECTBOX:
                opts = q.get("options") or []
                responses[key] = st.selectbox(display_label, opts, key=key)
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
