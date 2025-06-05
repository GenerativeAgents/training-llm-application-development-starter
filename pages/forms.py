import json
import os
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, TypedDict

import streamlit as st


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


# 質問一覧の定義
QUESTIONS_DAY1_CHECK: List[Question] = [
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

QUESTIONS_DAY2_CHECK: List[Question] = [
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
        "name": "lcel_explanation",
        "type": QuestionType.RADIO,
        "label": "LangChainのLCEL記法について、正しいものを1つ選択してください。",
        "options": [
            "LCELでは、処理を直列に接続するだけでなく、並列に接続することもできます。",
            "LangSmithにより処理の流れをトレースするためには、LCELを使う必要があります。",
            "LCELはLangChain専用の記法ではありません。LangChainを使わない開発でも利用できます。",
        ],
        "required": True,
    },
    {
        "name": "rag_document_limitation",
        "type": QuestionType.MULTISELECT,
        "label": "RAGのハンズオンでは、すべての文書をLLMに伝えるのではなく検索で該当した文書のみをLLMに渡しました。すべての文書を渡す形にしない理由について、正しいものを「すべて」選択してください。",
        "options": [
            "すべての文書を渡してしまうと消費するトークン数が大きくなり、コストが大きくなります。また、利用モデルの入力トークン数上限を超える量は渡すこともできません。そのため、必要な文書のみを渡す形が有効です。",
            "関係のない文書までLLMに渡してしまうと、LLMはそれらの内容にも注目してしまい回答精度が落ちてしまうこともあります。そのため、必要な文書のみを渡す形が有効な場合があります。",
            "Embeddingモデルを使ったベクトル検索では、回答に必要な文章を確実に検索することができ、すべての文書をLLMに渡すよりも少ないトークン数で確実に正しい回答を生成できます。そのため、必要な文書のみを渡す形が有効です。",
        ],
        "required": True,
    },
    {
        "name": "hyde_explanation",
        "type": QuestionType.RADIO,
        "label": "RAGの工夫の1つとしてHyDEを学びました。これは、ユーザーの入力内容をクエリーにしてベクトル検索するのではなく、手前でLLMに仮想の回答文を生成させて、それをクエリーにベクトル検索する手法です。このHyDEについて、正しいものを1つ選択してください。",
        "options": [
            "最初にLLMに生成させる仮想回答の精度が重要です。これが少しでも間違っていると、ユーザーの入力をそのまま使うよりも精度が落ちてしまいます。そのため、外部情報を与えない状態のLLMでも正しい回答を生成できる場合にのみ適した手法です。",
            "仮想回答を生成することで、ユーザーの入力に対して回答文で使われるであろうキーワードや表現などを補うことができ、ベクトル検索の際に目的の文書との距離が近づくので検索精度の向上を期待できます。仮想回答はキーワードや表現を補うものであり、必ずしも正解の必要はありません。",
            "仮想回答を生成してクエリーに使うことで、どんな場面でも精度の向上が見込めます。精度が悪化することはありません。そのため、仮想回答の生成コストが問題にならない場合は、常にこの手法を組み込んでおくべきです。",
        ],
        "required": True,
    },
    {
        "name": "rerank_reason",
        "type": QuestionType.MULTISELECT,
        "label": "RAGの工夫の1つとしてリランクを学びました。これは検索結果の順位を並び替える処理ですが、すでにベクトル検索した段階で文書は類似度順に並んでいるはずです。これをさらにリランクするのはなぜでしょうか。理由について正しいものを「すべて」選択してください。",
        "options": [
            "ベクトル検索では大量の文書を検索するため、速度を重視して類似度を算出します。そのため、類似度はいわば概算であり精度が高くはありません。これに対してリランクで使うモデルは精度を重視するために時間がかかり、大量の文書には適用できません。そのため、まずベクトル検索で文書の量を絞り、リランクモデルで精度を上げる形が有効です。",
            "リランクは、RAG-Fusionのような複数の検索クエリで検索した結果を融合するために必要な手法です。クエリが1つしかない場合、検索結果はすでにベクトルの類似度順で並んでいますので、それをリランクしても並びは変わらず意味がありません。",
            "リランクでは、手前の検索とは別の観点で結果を並べ替えることもできます。たとえば、ベクトル検索した結果に対して公開日順に並び替えて、新しい情報を重視する形でLLMに回答文を生成させることができます。リランクの仕組みは手前のベクトル検索と必ずしも一致させる必要はありません。",
        ],
        "required": True,
    },
    {
        "name": "offline_evaluation",
        "type": QuestionType.RADIO,
        "label": "オフライン評価について、正しいものを1つ選択してください。",
        "options": [
            "オフライン評価で期待した精度を出すことができれば、本番環境でも同様の精度を期待することができます。",
            "LangSmithを使用したオフライン評価では、ハンズオンで使用したRagasの評価メトリクス以外にも、独自の評価メトリクスを使うことができます。",
            "オフライン評価では、人手で作成したデータセットや本番データに基づくデータセットではなく、LLMで生成したデータセットを使用することが推奨されています。",
        ],
        "required": True,
    },
    {
        "name": "ai_agent_explanation",
        "type": QuestionType.MULTISELECT,
        "label": "AIエージェントについて、正しいものを「すべて」選択してください。",
        "options": [
            "1つのプロンプトで複雑な指示をするのではなく、ワークフローを組んでいくつかのプロンプトでタスクを進めるような構成を「Agentic Workflow」と呼びます。",
            "LLMの保有知識だけで処理するのではなく、外部の情報を取り込んで処理するのがAIエージェントです。",
            "「現在の通常のAI」と「AIエージェント」には明確な境界があるとするのではなく、複雑な目標を複雑な環境で適応的に達成する度合いを「エージェントらしさ（Agenticness）」として捉える場合があります。",
        ],
        "required": True,
    },
    {
        "name": "shell_tool_caution",
        "type": QuestionType.RADIO,
        "label": "LangGraphのcreate_react_agentを使ったハンズオンでShellToolを使うエージェントを作りましたが、ShellToolを利用する際の注意事項として正しいものを1つ選択してください。",
        "options": [
            "デフォルトでは実行できるコマンドが制限されているので、やりたい操作を実行できないことがあります。必要に応じて制限を解除する必要があります。",
            "コマンドをなんでも実行できてしまうので、サンドボックス環境を用意したり実行前に人間が確認できるようにしたりする対応が必要です。",
            "実行するコマンドの内容はLLMが決めるため、古いLLMのモデルで使うのは危険です。最近の性能が向上したモデルを使えば特に危険はありません。",
        ],
        "required": True,
    },
    {
        "name": "langgraph_explanation",
        "type": QuestionType.MULTISELECT,
        "label": "LangGraphについて、正しいものを「すべて」選んでください。",
        "options": [
            "LangGraphでは、ループや分岐を含むワークフローを、ノードとエッジによるグラフとして実装します。",
            "ワークフローに分岐が含まれているとLangChainだけでは実装できないため、必ずLangGraphを使う必要があります。",
            "ワークフローにループが含まれているとLangChainだけでは実装できませんが、LangGraphであれば実装できます。",
        ],
        "required": True,
    },
    {
        "name": "rag_implementation_challenges",
        "type": QuestionType.TEXT_AREA,
        "label": "もし仮に、本日学んだ内容をベースに社内資料を活用したRAGアプリケーションを開発する場合（たとえば社内規定の資料をベースに各種申請についての質問に答えてくれるアプリケーションなど）、どんなことが課題になりそうでしょうか。思いつくものを列挙してください。",
        "options": None,
        "required": True,
    },
]

QUESTIONS_DAY3_CHECK: List[Question] = [
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
        "name": "multi_agent_explanation",
        "type": QuestionType.RADIO,
        "label": "マルチエージェントについて、正しいものを1つ選択してください。",
        "options": [
            "マルチエージェントでは、ユーザーの入力をSupervisorが受け付けて、Supervisorが適当なエージェントを呼び出す構成を実装する場合があります。",
            "マルチエージェントでは、各エージェントで異なるモデルを使用する必要があります。",
            "LangGraphではマルチエージェントの実装はサポートされていません。",
        ],
        "required": True,
    },
    {
        "name": "human_in_the_loop",
        "type": QuestionType.RADIO,
        "label": "LangGraphでのHuman-in-the-Loopの実装について、正しいものを1つ選択してください。",
        "options": [
            "LangGraphのHuman-in-the-Loop機能は、ツール利用の承認を求める処理のみがサポートされており、人間に追加情報を求める処理を実装することはできません。",
            "人間からフィードバックがあった際にワークフローを続きから再開できるよう、Checkpointer機能を使用して実現されています。",
            "LangGraphで実装したワークフローをWebアプリケーションとして公開する場合は、Human-in-the-Loop機能を使うことはできません。",
        ],
        "required": True,
    },
    {
        "name": "ambient_agents",
        "type": QuestionType.RADIO,
        "label": "Ambient AgentsとAgent Inboxについて、正しいものを1つ選択してください。",
        "options": [
            "LangChainが提唱する「Ambient Agents」は、外部のサービスやデータに接続しながらタスクを遂行するようなAIエージェントを指します。",
            "LangChainが提唱する「Ambient Agents」は、複数のAIエージェントが強調動作する構成を指します。",
            "Human-in-the-LoopのためにInterrupt状態のスレッド一覧を「Agent Inbox」で表示することで、AIエージェントから人間への作業依頼に効率的に対応できる場合があります。",
        ],
        "required": True,
    },
    {
        "name": "long_term_memory",
        "type": QuestionType.RADIO,
        "label": "LLMエージェントの長期記憶について、正しいものを1つ選択してください。",
        "options": [
            "LangGraphは短期記憶のみをサポートしており、長期記憶はサポートしていません。",
            "LLMエージェントの長期記憶は、Embeddingモデルを使ったベクトル検索で実装することがベストプラクティスとされています。",
            "LLMエージェントの長期記憶では、人間が睡眠中に記憶を整理するように、ときどき記憶を整理する実装が有用な場合があります。",
        ],
        "required": True,
    },
    {
        "name": "computer_use",
        "type": QuestionType.RADIO,
        "label": "Computer useについて、正しいものを1つ選択してください。",
        "options": [
            "OpenAIやAnthropicのAPIでComputer use機能を使用すると、OpenAIやAnthropicの環境に立ち上がった仮想マシンをLLMに自動操作させることができます。",
            "OpenAIやAnthropicのAPIでComputer use機能では、LLMはマウスを移動する座標などを出力してくるだけであり、実際のコンピュータの操作はPythonなどのプログラムで実施することになります。",
            "OpenAIやAnthropicのAPIでComputer use機能では、ベンチマークで人間と同等のスコアを達成しています。",
        ],
        "required": True,
    },
    {
        "name": "single_pass_plan_generator",
        "type": QuestionType.RADIO,
        "label": "エージェントデザインパターンの「シングルパスプランジェネレーター」について、正しいものを1つ選択してください。",
        "options": [
            "エージェントが最初にタスクをサブタスクに分割し、サブタスクを順に実行していきます。",
            "各ステップでいくつかのプランを出し、毎回ユーザーに選んでもらいながら進めます。",
            "いくつもの別エージェントにプランを作らせ、投票で決まった案だけを使います。",
        ],
        "required": True,
    },
    {
        "name": "self_reflection",
        "type": QuestionType.RADIO,
        "label": "エージェントデザインパターンの「セルフリフレクション」について、正しいものを1つ選択してください。",
        "options": [
            "エージェントの出力をそのエージェント自身がチェックしてフィードバックします。",
            "エージェントの出力を別のエージェントがチェックしてフィードバックします。",
            "エージェントの出力を人間がチェックしてフィードバックします。",
        ],
        "required": True,
    },
    {
        "name": "mcp_explanation",
        "type": QuestionType.RADIO,
        "label": "MCPについて、正しいものを1つ選択してください。",
        "options": [
            "MCPの登場により、AIエージェントが外部のサービスやデータに接続できるようになりました。",
            "MCPは、AIエージェントが外部のサービスやデータに接続するために利用可能なプロトコルです。",
            "AIエージェントを実装するときは、できるだけMCPをサポートするべきです。",
        ],
        "required": True,
    },
]

QUESTIONS_SURVEY: List[Question] = [
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


QUESTIONS = {
    "DAY1_理解度テスト": QUESTIONS_DAY1_CHECK,
    "DAY2_理解度テスト": QUESTIONS_DAY2_CHECK,
    "DAY3_理解度テスト": QUESTIONS_DAY3_CHECK,
    "アンケート": QUESTIONS_SURVEY,
}

# 保存先 JSON ファイルパス
FILE_PATH = "responses.json"


def app() -> None:
    """
    Streamlit アプリのメイン処理
    """
    st.title("理解度テスト")

    # 質問一覧の選択
    survey_name = st.selectbox("質問一覧", list(QUESTIONS.keys()))

    if not survey_name:
        return

    # レスポンス格納用
    responses: Dict[str, str] = {}

    with st.form("survey_form"):
        questions = QUESTIONS[survey_name]
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

    if not submitted:
        return

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
