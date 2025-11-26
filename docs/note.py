import marimo

__generated_with = "0.18.1"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    mo.md(r"""
    ## 概要

    マルチホップの実装パターンを色々試してみる


    ## 解きたい問題の例

    「アンギラの国際通話の料金を教えてください。」


    ## 擬似的なベクトルDB検索関数

    最初に「アンギラ」で検索すると「国別料金表3」に情報があることがわかる。
    その後「国別料金表3」で検索すると「9999円/1分」という情報が得られる

    ```python
    TABLE_TERMS = ("国別料金表3", "table 3")
    TABLE_RESPONSE = "アンギラの国際通話料金は9999円/1分です。"

    ANGUILLA_TERMS = ("アンギラ", "anguilla", "angila", "angira")
    ANGUILLA_RESPONSE = "アンギラの国際通話料金は国別料金表3に記載されています。"

    UNKNOWN_RESPONSE = "情報が見つかりませんでした。"

    def search_documents(keywords: str) -> list[str]:
        if _fuzzy_contains(keywords, TABLE_TERMS):
            response = TABLE_RESPONSE
        elif _fuzzy_contains(keywords, ANGUILLA_TERMS):
            response = ANGUILLA_RESPONSE
        else:
            response = UNKNOWN_RESPONSE

        print(">>> search_documents called")
        rprint({"keywords": keywords, "response": response})
        return [response]
    ```


    ## システムプロンプト

    ```
    あなたは優秀な情報検索者です。

    与えられたツールを使って情報を検索しユーザの質問に答えてください。
    検索された情報に不足があれば、再度検索を行っても構いません。
    ```


    ## 実装パターン

    ### tool callを連続的に行ってマルチホップ行うパターン

    multi_hop_with_multi_tool_call.py


    ```python
    def gen_multi_hop_gpt5(input_org, model, effort, verbosity):
        "\"\"gpt5系のapiコール"\"\"
        input = copy.deepcopy(input_org)
        for i in range(MAX_FUNCTION_CALLS):
            rprint(f">>> Iteration {i + 1}/{MAX_FUNCTION_CALLS}")
            rprint(input)
            response = client.responses.create(
                model=model,
                reasoning={
                    "effort": effort
                },
                text={
                    "verbosity": verbosity
                },
                input=input,
                tools=tools,
            )
            input += response.output

            # 関数呼び出しの処理
            has_function_call = False
            for item in response.output:
                if item.type == "function_call" and item.name == "search_documents":
                    documents = search_documents(**json.loads(item.arguments))
                    input.append({
                        "type": "function_call_output",
                        "call_id": item.call_id,
                        "output": json.dumps({
                          "documents": documents
                        })
                    })
                    has_function_call = True

            # 関数呼び出しがなければ結果を返す
            if not has_function_call:
                return response.output

        # 最大試行回数に達した場合
        print(f"警告: 最大試行回数({MAX_FUNCTION_CALLS})に達しました")
        return response.output
    ```

    - 結果

    gpt-4.1だと1hopで終わってしまう。

    ```python
    {
        'model': 'gpt-4.1-2025-04-14',
        'plan': [
            ResponseOutputMessage(
                id='msg_08056a3d1818db0e0069264cd21000819cac59e0462316346b',
                content=[
                    ResponseOutputText(
                        annotations=[],
                        text='アンギラの国際通話料金は「国別料金表」という資料に記載されています。具体的な料金をお知りになりたい場合は、ご利用されている通信会社の国際通話料金表をご確認ください。もし特定の通信会社（NTT、ソフトバンク、au等）をご指定いた
    だければ、さらに詳細な料金を調べることも可能です。',
                        type='output_text',
                        logprobs=[]
                    )
                ],
                role='assistant',
                status='completed',
                type='message'
            )
        ]
    }
    ```


    gpt5だと

    ```
    {'keywords': 'Angilla international call rates Anguilla phone rates', 'response': '情報が見つかりませんでした。'}
    警告: 最大試行回数(5)に達しました
    {
        'model': 'gpt-5-nano-2025-08-07',
        'effort': 'minimal',
        'verbosity': 'low',
        'output': [
            ResponseReasoningItem(id='rs_02ab1f32fc1696be0069264cda016c8195a8d9d5d1e901cb49', summary=[], type='reasoning', content=None, encrypted_content=None, status=None),
            ResponseFunctionToolCall(
                arguments='{"keywords":"Angilla international call rates Anguilla phone rates"}',
                call_id='call_6EQYO42YpifxaOi1XnhmJs3Q',
                name='search_documents',
                type='function_call',
                id='fc_02ab1f32fc1696be0069264cda32b08195a45af5231051effb',
                status='completed'
            )
        ]
    }
    ```

    ```
    {
        'model': 'gpt-5-nano-2025-08-07',
        'effort': 'minimal',
        'verbosity': 'high',
        'output': [
            ResponseReasoningItem(id='rs_04449624b7833cd50069264ce01fb88197a5aebea0bc64a8e1', summary=[], type='reasoning', content=None, encrypted_content=None, status=None),
            ResponseOutputMessage(
                id='msg_04449624b7833cd50069264ce03f508197a17964601f763376',
                content=[
                    ResponseOutputText(
                        annotations=[],
                        text='現時点でご希望の「アンギラ（Anguilla）の国際通話料金」について、私の手元の情報源から直接確認できませんでした。以下の点を確認させてください。必要であれば、追加検索も実施します。\n\n-
    どの通信事業者を想定していますか？（例：現地の携帯キャリア、固定電話事業者、米国の大手キャリア、国際プリペイドカード等）\n- 国際通話の相手先を特定しますか？（例：特定の国・地域、国際電話番号への掛け方の料金など）\n-
    料金の形式は「1分あたりの料金（通常料金）」、「キロバイト値引き付きのプリペイド料金」、「接続料金＋通話料金の組み合わせ」など、どの形を知りたいですか？\n-
    具体的な時期の料金をご希望ですか？（料金は規制やプロモーションで変動します）\n\nもし最新の料金をすぐに知りたい場合は、次のいずれかの方法をとるのがおすすめです。\n- アンギラの主要キャリア（例：Digicel Anguilla、Flow Anguilla
    など）公式サイトの国際通話料金ページを確認\n- 利用中の現地/国際電話プランの「料金表」や「料金ガイド」を確認\n-
    あなたが使っている通信サービス（携帯、固定、VoIP、プリペイド等）を教えていただければ、該当する料金情報を優先して調べます\n\n追加情報をいただければ、最新かつ具体的な料金を調べてご案内します。',
                        type='output_text',
                        logprobs=[]
                    )
                ],
                role='assistant',
                status='completed',
                type='message'
            )
        ]
    }
    ```

    ```
    {'keywords': 'Anguilla country code +1 264 international calling rates', 'response': '情報が見つかりませんでした。'}
    警告: 最大試行回数(5)に達しました
    {
        'model': 'gpt-5-nano-2025-08-07',
        'effort': 'high',
        'verbosity': 'low',
        'output': [
            ResponseReasoningItem(id='rs_0736ee6c05dc9b640069264cfc49a481a39dcf2f870f1ad21f', summary=[], type='reasoning', content=None, encrypted_content=None, status=None),
            ResponseFunctionToolCall(
                arguments='{"keywords":"Anguilla country code +1 264 international calling rates"}',
                call_id='call_9LxvibNvhT5eyYql5kBIFGOk',
                name='search_documents',
                type='function_call',
                id='fc_0736ee6c05dc9b640069264cfc9ea081a3ac526c43284de700',
                status='completed'
            )
        ]
    }
    ```
    """)
    return


if __name__ == "__main__":
    app.run()
