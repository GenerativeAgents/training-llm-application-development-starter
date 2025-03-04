# training-llm-application-development-starter

LLM アプリケーション開発者養成講座のハンズオン環境構築のためのリポジトリです。

## ハンズオン環境の準備

AWS の EC2 インスタンスで code-server (ブラウザ上で動作する Visual Studio Code) を使うハンズオン環境を使用します。

![](./docs/images/ec2_code_server/code_server.png)

ハンズオン環境には付与された接続情報で接続するか、[こちら](./docs/ec2_code_server.md) の手順で構築してください。

## 各種ダウンロード・インストール

### ターミナルを開く

画面左のメニューボタン (≡) をクリックし、「ターミナル」>「新しいターミナル」でターミナルを開くことができます。

![](./docs/images/ec2_code_server/code_server_terminal.png)

### ソースコードのダウンロード

以下のコマンドでこのリポジトリのソースコードをダウンロードしてください。

```console
git clone https://github.com/GenerativeAgents/training-llm-application-development-starter.git
```

cd コマンドでディレクトリを移動してください。

```console
cd training-llm-application-development-starter
```

> [!NOTE]
> 以後のコマンドはすべて training-llm-application-development-starter ディレクトリで実行します。

### uv のインストール

Python の特定バージョンのインストールやパッケージの管理のため、[uv](https://github.com/astral-sh/uv) をインストールします。
以下のコマンドを実行してください。

```console
curl -LsSf https://astral.sh/uv/0.4.14/install.sh | sh
```

上記のスクリプトによる `~/.bashrc` の変更を反映するため、以下のコマンドでシェルを起動しなおしてください。

```console
exec "$SHELL"
```

以下のコマンドで uv のバージョンが表示されれば、インストール完了です。

```console
uv --version
```

### Python と Python パッケージのインストール

uv で Python と Python パッケージをインストールします。
以下のコマンドを実行してください。

```console
uv sync
```

以下のコマンドで Python のバージョンが表示されるか確認してください。

```console
uv run python --version
```

### langchain リポジトリの clone

講座の一部で langchain リポジトリのデータを読み込んで使います。

以下のコマンドを実行して、langchain リポジトリを clone してください。

```console
git clone --depth 1 https://github.com/langchain-ai/langchain.git ./tmp/langchain
```

## エディタの起動

左上のメニューから「File」>「Open Folder」で「/home/ubuntu/environment/training-llm-application-development-starter」を開いてください。

![](./docs/images/code_server_open_folder.png)

以下の画像のように、「training-llm-application-development-starter」ディレクトリでエディタが開かれたことを確認してください。

![](./docs/images/code_server_open_folder_completed.png)

## Jupyter のセットアップ (Visual Studio Code の Jupyter 拡張機能)

Visual Studio Code の画面左の「Extensions」を開いて、「RECOMMENDED」の拡張機能をすべてインストールしてください。

![](./docs/images/code_server_extensions.png)

「notebooks/hello.ipynb」を開いてください。

![](./docs/images/code_server_notebook.png)

セルにフォーカスして実行 (Shift + Enter) すると、「Select Kernel」というメニューが開きます。
「Python Environments...」を選択してください。

![](./docs/images/code_server_notebook_select_kernel.png)

Python の環境として「.venv (venv/bin/python)」を選択してください。

![](./docs/images/code_server_notebook_select_kernel_venv.png)

その後、「hello.ipynb」の内容が想定通り動作するか確認してください。

![](./docs/images/code_server_notebook_hello.png)

## Streamlit の起動

以下のコマンドで Streamlit を起動してください。

```console
make streamlit
```

> [!INFO]
> Streamlit の起動時に Email の入力が求められた場合、入力せず空のまま Enter で進めてください。

ターミナル上で Web アプリケーション等を起動した場合、画面右下に表示される「Open in Browser」をクリックするとプレビューできます。

![](./docs/images/ec2_code_server/code_server_port_forward.png)

または、`https://<ランダムな文字列>.cloudfront.net/proxy/<ポート番号>/` にアクセスすることでも、Web アプリケーションのプレビューが可能です。

Streamlit のアプリケーションにアクセスしたら、下部の入力欄に適当な入力をして、応答が表示されるか確認してください。

![](./docs/images/streamlit_hello_world.png)

これでハンズオン環境の準備は完了です。

### Streamlitの停止

Streamlit がすでに起動している場合、`make streamlit` を実行すると以下のエラーが発生します。
```
$ make streamlit
uv run streamlit run app.py --server.port 8080
2025-03-04 20:40:42.479 Port 8080 is already in use
make: *** [streamlit] Error 1
```

この場合は、`pkill streamlit` を実行して Streamlit を停止してください。
