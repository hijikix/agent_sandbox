import marimo

__generated_with = "0.18.4"
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
    ### tool callを連続的に行ってマルチホップ行うパターン(previous_response_idを使う)
    """)
    return


@app.cell
def _():
    # GPT4系のモデル
    GPT4_MODELS = [
        "gpt-4.1-2025-04-14",
    ]
    return (GPT4_MODELS,)


@app.cell
def _():
    # GPT5系のモデル
    GPT5_MODELS = [
        "gpt-5-nano-2025-08-07",
        # "gpt-5-mini-2025-08-07",
        # "gpt-5-2025-08-07",
    ]

    # APIコール時のパラメータもパターンを用意する
    GPT5_REASONING_EFFORTS = [
        'minimal',
        # 'low',
        # 'medium',
        'high',
    ]

    GPT5_TEXT_VERBOSITIES = [
        'low',
        # 'medium',
        'high',
    ]
    return GPT5_MODELS, GPT5_REASONING_EFFORTS, GPT5_TEXT_VERBOSITIES


@app.cell
def _():
    from openai import OpenAI
    from pydantic import BaseModel
    from tools import search_documents_raw, tools

    client = OpenAI()
    return client, search_documents_raw, tools


@app.cell
def _():
    MAX_FUNCTION_CALLS = 5
    return (MAX_FUNCTION_CALLS,)


@app.cell
def _(
    MAX_FUNCTION_CALLS,
    client,
    copy,
    json,
    rprint,
    search_documents_raw,
    tools,
):
    def gen_multi_hop_gpt4(input_org, model):
        """gpt4系のapiコール"""
        input = copy.deepcopy(input_org)
        for i in range(MAX_FUNCTION_CALLS):
            rprint(f">>> Iteration {i + 1}/{MAX_FUNCTION_CALLS}")
            response = client.responses.create(
                model=model,
                input=input,
                tools=tools,
            )
            input += response.output

            # 関数呼び出しの処理
            has_function_call = False
            for item in response.output:
                if item.type == "function_call" and item.name == "search_documents":
                    documents = search_documents_raw(**json.loads(item.arguments))
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
    return (gen_multi_hop_gpt4,)


@app.cell
def _(
    MAX_FUNCTION_CALLS,
    client,
    copy,
    json,
    rprint,
    search_documents_raw,
    tools,
):
    def gen_multi_hop_gpt5(input_org, model, effort, verbosity):
        """gpt5系のapiコール"""
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
                    documents = search_documents_raw(**json.loads(item.arguments))
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
    GPT4_MODELS,
    GPT5_MODELS,
    GPT5_REASONING_EFFORTS,
    GPT5_TEXT_VERBOSITIES,
    gen_multi_hop_gpt4,
    gen_multi_hop_gpt5,
    product,
    rprint,
):
    def _():
        SYSTEM_PROMPT = """
    あなたは優秀な検索エージェントです。

    与えられたツールを使って情報を検索しユーザの質問に答えてください。
    内部知識は使わずにツールから取得した情報のみを使って答えるようにしてください。

    検索された情報に不足があれば、再度検索を行っても構いません。
    """

        USER_PROMPT = """
    ネクサス3000に搭載されているCPUの製造元の本社所在地は？
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

        for model in GPT4_MODELS:
            print(f"### {model} ###")
            plan = gen_multi_hop_gpt4(input, model)
            rprint({
                "model": model,
                "plan": plan,
            })

        # # 網羅的な組み合わせを生成
        combinations = list(product(GPT5_MODELS, GPT5_REASONING_EFFORTS, GPT5_TEXT_VERBOSITIES))

        # 結果を表示
        for i, (model, effort, verbosity) in enumerate(combinations, 1):
            print(f"### {model} effort: {effort} verbosity: {verbosity} ###")
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
