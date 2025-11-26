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

    gpt-4.1だとマルチホップせず、1 hopで終わってしまう。


    ```python
    ### gpt-4.1-2025-04-14 ###
    >>> Iteration 1/5
    >>> search_documents called
    {'keywords': 'アンギラ 国際通話 料金', 'response': 'アンギラの国際通話料金は国別料金表3に記載されています。'}
    >>> Iteration 2/5
    {
        'model': 'gpt-4.1-2025-04-14',
        'plan': [
            ResponseOutputMessage(
                id='msg_04aeb1f87d9f1530006926667a60c4819e83aa0ded7bfbbf9d',
                content=[
                    ResponseOutputText(
                        annotations=[],
                        text='アンギラの国際通話料金は、「国別料金表」に記載されています。詳細な料金をお知りになりたい場合は、ご利用の通信会社の国際通話「国別料金表」でアンギラの欄をご確認ください。
    もし具体的な通信会社名やサービス名があれば、さらに詳しく調べることも可能です。',
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


    gpt5

    - gpt-5-nanoはイテレーションはするが、「国別料金表3」で再検索などは行なってくれない
      単純に賢さが足りない?

    - gpt-5は「effort: minimal」だと割とうまくいくが、「effort: high」だとうまくいかない
      「effort: high」の場合、質問の背景なども考慮してしまい満足な回答を出せずに困っているイメージ
      「effort: minimal」だと考える時間が無く、即答に近い形なのでうまくいく？


    ```
    ### gpt-5-nano-2025-08-07 effort: minimal verbosity: low ###
    >>> Iteration 1/5
    >>> search_documents called
    {'keywords': 'Angila international call rates', 'response': 'アンギラの国際通話料金は国別料金表3に記載されています。'}
    >>> Iteration 2/5
    >>> search_documents called
    {'keywords': 'Angila international call rates Anguilla?', 'response': 'アンギラの国際通話料金は国別料金表3に記載されています。'}
    >>> Iteration 3/5
    >>> search_documents called
    {'keywords': 'Anguilla international calling rates', 'response': 'アンギラの国際通話料金は国別料金表3に記載されています。'}
    >>> Iteration 4/5
    >>> search_documents called
    {'keywords': 'Anguilla international calling rates per minute', 'response': 'アンギラの国際通話料金は国別料金表3に記載されています。'}
    >>> Iteration 5/5
    >>> search_documents called
    {'keywords': 'Anguilla international calling price per minute', 'response': 'アンギラの国際通話料金は国別料金表3に記載されています。'}
    警告: 最大試行回数(5)に達しました
    {
        'model': 'gpt-5-nano-2025-08-07',
        'effort': 'minimal',
        'verbosity': 'low',
        'output': [
            ResponseReasoningItem(id='rs_00fafc7971f1a9370069266681d4f08191963d088e3e6b2103', summary=[], type='reasoning', content=None, encrypted_content=None, status=None),
            ResponseFunctionToolCall(
                arguments='{"keywords":"Anguilla international calling price per minute"}',
                call_id='call_9ekqwIe0K6zOnv2OK8DJSDAL',
                name='search_documents',
                type='function_call',
                id='fc_00fafc7971f1a93700692666821830819195226d2f89ffd618',
                status='completed'
            )
        ]
    }
    ### gpt-5-nano-2025-08-07 effort: minimal verbosity: high ###
    >>> Iteration 1/5
    >>> search_documents called
    {'keywords': 'Angila international calling rates', 'response': 'アンギラの国際通話料金は国別料金表3に記載されています。'}
    >>> Iteration 2/5
    >>> search_documents called
    {'keywords': 'Angila 国際通話 料金', 'response': 'アンギラの国際通話料金は国別料金表3に記載されています。'}
    >>> Iteration 3/5
    >>> search_documents called
    {'keywords': 'Angila international calling rates Angila', 'response': 'アンギラの国際通話料金は国別料金表3に記載されています。'}
    >>> Iteration 4/5
    >>> search_documents called
    {'keywords': 'アンギラ 国際通話 料金 アンギラ', 'response': 'アンギラの国際通話料金は国別料金表3に記載されています。'}
    >>> Iteration 5/5
    >>> search_documents called
    {'keywords': 'Angila international calling rates site:example.com', 'response': 'アンギラの国際通話料金は国別料金表3に記載されています。'}
    警告: 最大試行回数(5)に達しました
    {
        'model': 'gpt-5-nano-2025-08-07',
        'effort': 'minimal',
        'verbosity': 'high',
        'output': [
            ResponseReasoningItem(id='rs_079f84986940b7b400692666868bd881a2866a73f204d72f45', summary=[], type='reasoning', content=None, encrypted_content=None, status=None),
            ResponseFunctionToolCall(
                arguments='{"keywords":"Angila international calling rates site:example.com"}',
                call_id='call_9qCwWeTTin3GXE3p3xGVtg1j',
                name='search_documents',
                type='function_call',
                id='fc_079f84986940b7b40069266686a9b481a29db6032d31522158',
                status='completed'
            )
        ]
    }
    ### gpt-5-nano-2025-08-07 effort: high verbosity: low ###
    >>> Iteration 1/5
    >>> search_documents called
    {'keywords': 'アンギラ 国際通話 料金', 'response': 'アンギラの国際通話料金は国別料金表3に記載されています。'}
    >>> search_documents called
    {'keywords': 'Anguilla international calling rates', 'response': 'アンギラの国際通話料金は国別料金表3に記載されています。'}
    >>> Iteration 2/5
    >>> search_documents called
    {'keywords': 'Anguilla international calling rate', 'response': 'アンギラの国際通話料金は国別料金表3に記載されています。'}
    >>> search_documents called
    {'keywords': 'Anguilla international call rates per minute', 'response': 'アンギラの国際通話料金は国別料金表3に記載されています。'}
    >>> search_documents called
    {'keywords': 'アンギラ 国際通話 料金 日本', 'response': 'アンギラの国際通話料金は国別料金表3に記載されています。'}
    >>> Iteration 3/5
    {
        'model': 'gpt-5-nano-2025-08-07',
        'effort': 'high',
        'verbosity': 'low',
        'output': [
            ResponseReasoningItem(id='rs_003a984af1d4b0e200692666997aa8819780887ba8d4bd20d0', summary=[], type='reasoning', content=None, encrypted_content=None, status=None),
            ResponseOutputMessage(
                id='msg_003a984af1d4b0e200692666a1ffd4819792b03c5a2280362b',
                content=[
                    ResponseOutputText(
                        annotations=[],
                        text='どの発信元からの料金を知りたいですか？日本からアンギラへかける料金ですか、それともアンギラ発の国際通話料金ですか？また、特定のキャリアを教えてください。現在のデータベースには具体的な料金が見つかっていません。発信元とキャ
    リアを教えていただければ最新情報を調べます。',
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
    ### gpt-5-nano-2025-08-07 effort: high verbosity: high ###
    >>> Iteration 1/5
    >>> search_documents called
    {'keywords': 'アンギラ 国際通話 料金', 'response': 'アンギラの国際通話料金は国別料金表3に記載されています。'}
    >>> search_documents called
    {'keywords': 'Anguilla international calling rates', 'response': 'アンギラの国際通話料金は国別料金表3に記載されています。'}
    >>> search_documents called
    {'keywords': 'Anguilla international call rates', 'response': 'アンギラの国際通話料金は国別料金表3に記載されています。'}
    >>> search_documents called
    {'keywords': 'Anguilla 国際電話 料金', 'response': 'アンギラの国際通話料金は国別料金表3に記載されています。'}
    >>> Iteration 2/5
    >>> search_documents called
    {'keywords': '国別料金3', 'response': 'アンギラの国際通話料金は9999円/1分です。'}
    >>> Iteration 3/5
    >>> search_documents called
    {'keywords': 'アンギラ 国際通話料金 1分', 'response': 'アンギラの国際通話料金は国別料金表3に記載されています。'}
    >>> Iteration 4/5
    >>> search_documents called
    {'keywords': '9999円 アンギラ 国際通話', 'response': 'アンギラの国際通話料金は国別料金表3に記載されています。'}
    >>> Iteration 5/5
    >>> search_documents called
    {'keywords': '円/分 アンギラ 国際通話', 'response': 'アンギラの国際通話料金は国別料金表3に記載されています。'}
    警告: 最大試行回数(5)に達しました
    {
        'model': 'gpt-5-nano-2025-08-07',
        'effort': 'high',
        'verbosity': 'high',
        'output': [
            ResponseReasoningItem(id='rs_02b4e2d2f162b1d800692666b609b4819e81b596334dc71f8b', summary=[], type='reasoning', content=None, encrypted_content=None, status=None),
            ResponseFunctionToolCall(
                arguments='{"keywords":"円/分 アンギラ 国際通話"}',
                call_id='call_PeUj6WLsmOttQMf59goYOR9e',
                name='search_documents',
                type='function_call',
                id='fc_02b4e2d2f162b1d800692666b840e0819e9ddddd0c78010565',
                status='completed'
            )
        ]
    }
    ### gpt-5-2025-08-07 effort: minimal verbosity: low ###
    >>> Iteration 1/5
    >>> search_documents called
    {'keywords': 'アンギラ 国際通話 料金', 'response': 'アンギラの国際通話料金は国別料金表3に記載されています。'}
    >>> Iteration 2/5
    >>> search_documents called
    {'keywords': '国別料金表3 アンギラ 国際通話', 'response': 'アンギラの国際通話料金は9999円/1分です。'}
    >>> Iteration 3/5
    {
        'model': 'gpt-5-2025-08-07',
        'effort': 'minimal',
        'verbosity': 'low',
        'output': [
            ResponseReasoningItem(id='rs_070e7a42db7dd2db00692666bcd21c8195bc678f99febbd82e', summary=[], type='reasoning', content=None, encrypted_content=None, status=None),
            ResponseOutputMessage(
                id='msg_070e7a42db7dd2db00692666bd117c819589273c52d34fb0ba',
                content=[ResponseOutputText(annotations=[], text='アンギラへの国際通話料金は、1分あたり9999円です。', type='output_text', logprobs=[])],
                role='assistant',
                status='completed',
                type='message'
            )
        ]
    }
    ### gpt-5-2025-08-07 effort: minimal verbosity: high ###
    >>> Iteration 1/5
    >>> search_documents called
    {'keywords': 'アンギラ 国際通話 料金', 'response': 'アンギラの国際通話料金は国別料金表3に記載されています。'}
    >>> Iteration 2/5
    >>> search_documents called
    {'keywords': '国別料金表3', 'response': 'アンギラの国際通話料金は9999円/1分です。'}
    >>> Iteration 3/5
    {
        'model': 'gpt-5-2025-08-07',
        'effort': 'minimal',
        'verbosity': 'high',
        'output': [
            ResponseReasoningItem(id='rs_0c29b2deab65bfa600692666c2f2d081a382c14b0a098aaf55', summary=[], type='reasoning', content=None, encrypted_content=None, status=None),
            ResponseOutputMessage(
                id='msg_0c29b2deab65bfa600692666c32e8481a3947022c0570891ae',
                content=[
                    ResponseOutputText(
                        annotations=[],
                        text='以下は、ドキュメント検索に基づく情報です。\n\n- アンギラ（Anguilla）の国際通話料金：1分あたり
    9,999円\n\n出典：国別料金表3（検索結果より）\n\nご利用の通信事業者やプランによって料金は大きく異なる場合があります。上記は参照資料に基づく金額ですが、実際のご利用前に以下の点をご確認ください。\n-
    ご契約中のキャリア（例：NTTドコモ、au、ソフトバンク、格安SIM各社）の国際通話料金表\n- 国際通話オプション（かけ放題や割引パック）の有無\n- VoIPアプリ（Skype、LINE、WhatsApp など）での通話可否とデータ通信料\n- アンギラの国番号は +1-264
    です。発信時のダイヤル方法をご確認ください。\n\n必要であれば、ご利用中のキャリア名を教えていただければ、キャリア公式の最新の料金ページを確認して具体的な金額をお調べします。',
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
    ### gpt-5-2025-08-07 effort: high verbosity: low ###
    >>> Iteration 1/5
    >>> search_documents called
    {'keywords': 'アンギラ 国際通話 料金', 'response': 'アンギラの国際通話料金は国別料金表3に記載されています。'}
    >>> search_documents called
    {'keywords': '日本から アンギラ 国際電話 料金', 'response': 'アンギラの国際通話料金は国別料金表3に記載されています。'}
    >>> search_documents called
    {'keywords': 'docomo 国際電話 アンギラ 料金', 'response': 'アンギラの国際通話料金は国別料金表3に記載されています。'}
    >>> search_documents called
    {'keywords': 'au 国際電話 アンギラ 料金', 'response': 'アンギラの国際通話料金は国別料金表3に記載されています。'}
    >>> search_documents called
    {'keywords': 'ソフトバンク 国際電話 アンギラ 料金', 'response': 'アンギラの国際通話料金は国別料金表3に記載されています。'}
    >>> search_documents called
    {'keywords': '国番号 1-264 アンギラ 料金', 'response': 'アンギラの国際通話料金は国別料金表3に記載されています。'}
    >>> search_documents called
    {'keywords': 'Anguilla international calling rates Japan', 'response': 'アンギラの国際通話料金は国別料金表3に記載されています。'}
    >>> search_documents called
    {'keywords': 'Skype call rates Anguilla', 'response': 'アンギラの国際通話料金は国別料金表3に記載されています。'}
    >>> search_documents called
    {'keywords': 'LINE Out アンギラ 通話 料金', 'response': 'アンギラの国際通話料金は国別料金表3に記載されています。'}
    >>> Iteration 2/5
    >>> search_documents called
    {'keywords': '国別料金表3 アンギラ 国際通話 料金', 'response': 'アンギラの国際通話料金は9999円/1分です。'}
    >>> Iteration 3/5
    {
        'model': 'gpt-5-2025-08-07',
        'effort': 'high',
        'verbosity': 'low',
        'output': [
            ResponseReasoningItem(id='rs_08f0e5a56b50bc6100692666e66bf0819d901c7cc0b5eb2960', summary=[], type='reasoning', content=None, encrypted_content=None, status=None),
            ResponseOutputMessage(
                id='msg_08f0e5a56b50bc610069266706a0c8819d94df97b893544624',
                content=[
                    ResponseOutputText(
                        annotations=[],
                        text='どこからどこへの料金を知りたいですか？例: 日本からアンギラへ／アンギラから海外。あわせて利用キャリアやプラン（docomo/au/SoftBank、固定電話、IP通話など）も教えてください。',
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
    ### gpt-5-2025-08-07 effort: high verbosity: high ###
    >>> Iteration 1/5
    >>> search_documents called
    {'keywords': 'アンギラ 国際電話 料金', 'response': 'アンギラの国際通話料金は国別料金表3に記載されています。'}
    >>> Iteration 2/5
    >>> search_documents called
    {'keywords': 'NTT 0033 アンギラ 料金', 'response': 'アンギラの国際通話料金は国別料金表3に記載されています。'}
    >>> Iteration 3/5
    >>> search_documents called
    {'keywords': 'KDDI 001 アンギラ 料金', 'response': 'アンギラの国際通話料金は国別料金表3に記載されています。'}
    >>> Iteration 4/5
    >>> search_documents called
    {'keywords': 'アンギラ 国番号 1-264', 'response': 'アンギラの国際通話料金は国別料金表3に記載されています。'}
    >>> Iteration 5/5
    {
        'model': 'gpt-5-2025-08-07',
        'effort': 'high',
        'verbosity': 'high',
        'output': [
            ResponseReasoningItem(id='rs_078ec30c4ad6c1ad00692667391a5c8190998c0b6a59a07315', summary=[], type='reasoning', content=None, encrypted_content=None, status=None),
            ResponseOutputMessage(
                id='msg_078ec30c4ad6c1ad0069266756e2e48190973ab56f0816d1c1',
                content=[
                    ResponseOutputText(
                        annotations=[],
                        text='確認させてください。\n「アンギラの国際通話の料金」は、次のどれを知りたいでしょうか？\n- 日本からアンギラ（国番号＋1-264）へ発信する料金\n- アンギラから日本（または他国）へ発信する料金\n-
    それともローミング中（日本の携帯をアンギラで使う場合）の通話料金\n\nどの方向の通話か、発信元の国・回線（携帯なら docomo/au/SoftBank/Rakuten など、固定なら NTT
    など）、プラン名（わかれば）を教えていただければ、公式料金表を確認して具体的な1分あたりの料金、課金単位（30秒/60秒など）、接続料の有無まで調べてお伝えします。\n\nまず一般的な注意点だけお伝えします\n- 国番号: アンギラは
    +1-264（北米番号計画NANPの一部）です。日本からは 010-1-264-xxx-xxxx（または携帯なら +1-264-xxx-xxxx）で発信します。\n- 料金水準:
    米国/カナダ(+1)と同じ体系ではないことが多く、キャリヤやプランによっては「数百円/分」になるケースもあります。国際SMSも高額になりがちです。\n- 定額オプション:
    各社の「国際通話定額」は対象国が限られており、アンギラは対象外のことが多いです（要確認）。\n- 詐欺に注意: カリブ圏の一部ではワン切り等で高額な国際発信を誘導する詐欺が過去に報告されています。心当たりのない着信への折り返しには注意してください。\n-
    代替手段: 相手と双方でデータ通信が使えるなら、WhatsApp／LINE／FaceTime／Viber／Skype などのIP通話が安価（もしくは無料）です。固定・携帯番号へ発信する必要がある場合は「Skypeクレジット」「LINE
    Out」等の従量課金が携帯キャリア発信より安いことがあります。\n\nもし「日本の特定キャリア（例：docomo/au/SoftBank/楽天モバイル、NTTの固定電話など）からアンギラへ」の料金を知りたい場合は、次を教えてください。\n- 回線種別（携帯 or
    固定）とキャリア名\n- プラン名（国際通話オプション加入の有無）\n- 発信先（アンギラの固定電話 or 携帯）\n\nいただければ、最新の公式料金表を確認して具体的な金額をお調べします。',
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
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
