import marimo

__generated_with = "0.17.7"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import copy
    import json
    from itertools import product
    from rich import print as rprint
    return copy, json, mo, product, rprint


@app.cell
def _():
    from dotenv import load_dotenv

    load_dotenv()
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### 色々なパターンでマルチホップを行ってみます
    """)
    return


@app.cell
def _():
    # GPT4系のモデル
    GPT4_MODELS = [
        "gpt-4.1-2025-04-14",
    ]
    return


@app.cell
def _():
    # GPT5系のモデル
    GPT5_MODELS = [
        # "gpt-5-nano-2025-08-07",
        # "gpt-5-mini-2025-08-07",
        "gpt-5-2025-08-07",
    ]

    # APIコール時のパラメータもパターンを用意する
    GPT5_REASONING_EFFORTS = [
        # 'minimal',
        # 'low',
        'medium',
        # 'high',
    ]

    GPT5_TEXT_VERBOSITIES = [
        # 'low',
        'medium',
        # 'high',
    ]
    return GPT5_MODELS, GPT5_REASONING_EFFORTS, GPT5_TEXT_VERBOSITIES


@app.cell
def _(rprint):
    from openai import OpenAI
    from pydantic import BaseModel

    client = OpenAI()

    tools = [
        {
            "type": "function",
            "name": "search_documents",
            "description": "ドキュメントデータベースから情報を検索します",
            "parameters": {
                "type": "object",
                "properties": {
                    "keywords": {
                        "type": "string",
                        "description": "検索キーワード",
                    },
                },
                "required": ["keywords"],
            },
        },
    ]

    def search_documents(keywords):
        """
        keywords: "キーワード1, キーワード2, キーワード3..."
        """
        if '国別料金表3' in keywords:
            response = "アンギラの国際通話料金は9999円/1分です。"
        elif 'アンギラ' in keywords or "Angila" in keywords or "Angira" in keywords:
            response = "アンギラの国際通話料金は国別料金表3に記載されています。"
        elif '国別料金表3' in keywords:
            response = "アンギラの国際通話料金は9999円/1分です。"
        else:
            response = "情報が見つかりませんでした。"

        print(">>> search_documents called")
        rprint({
            'keywords': keywords,
            "response": response
        })
        return [response]
    return client, search_documents, tools


@app.cell
def _():
    MAX_FUNCTION_CALLS = 5
    return (MAX_FUNCTION_CALLS,)


@app.cell
def _(client, tools):
    def gen_multi_hop_gpt4(input, model):
        """gpt4系のapiコール"""
        response = client.responses.create(
            model=model,
            input=input,
            tools=tools,
        )
        output = response.output
        return output
    return


@app.cell
def _(MAX_FUNCTION_CALLS, client, copy, json, rprint, search_documents, tools):
    def gen_multi_hop_gpt5(input_org, model, effort, verbosity):
        """gpt5系のapiコール"""
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
    return (gen_multi_hop_gpt5,)


@app.cell
def _(mo):
    mo.md(r"""
    ### マルチホップ（シンプルなシステムプロンプト）
    """)
    return


@app.cell
def _(
    GPT5_MODELS,
    GPT5_REASONING_EFFORTS,
    GPT5_TEXT_VERBOSITIES,
    gen_multi_hop_gpt5,
    product,
    rprint,
):
    def _():
        SYSTEM_PROMPT = """
    あなたは優秀な情報検索者です。
    """

        USER_PROMPT = """
    アンギラの国際通話の料金を教えてください。
    """

        input = [
            {
                "role": "developer",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": USER_PROMPT
            }
        ]

        # for model in GPT4_MODELS:
        #     plan = gen_multi_hop_gpt4(input, model)
        #     rprint({
        #         "model": model,
        #         "plan": plan,
        #     })

        # 網羅的な組み合わせを生成
        combinations = list(product(GPT5_MODELS, GPT5_REASONING_EFFORTS, GPT5_TEXT_VERBOSITIES))

        # 結果を表示
        for i, (model, effort, verbosity) in enumerate(combinations, 1):
            output = gen_multi_hop_gpt5(input, model, effort, verbosity)
            rprint({
                "model": model,
                "effort": effort,
                "verbosity": verbosity,
                "output": output,
            })

    _()
    return


if __name__ == "__main__":
    app.run()
