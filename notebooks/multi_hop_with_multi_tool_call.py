import marimo

__generated_with = "0.18.1"
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
    ### tool callを連続的に行ってマルチホップ行うパターン
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
        "gpt-5-2025-08-07",
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

    from difflib import SequenceMatcher
    import re

    def _normalize(text: str) -> str:
        return text.lower()

    def _fuzzy_contains(
        keywords: str, terms: tuple[str, ...], threshold: float = 0.72
    ) -> bool:
        if not keywords:
            return False

        haystack = _normalize(keywords)
        normalized_terms = tuple(_normalize(term) for term in terms)

        if any(term in haystack for term in normalized_terms):
            return True

        tokens = [token for token in re.split(r"[\s,、。]+", haystack) if token]
        for token in tokens:
            for term in normalized_terms:
                if SequenceMatcher(None, token, term).ratio() >= threshold:
                    return True

        for term in normalized_terms:
            if SequenceMatcher(None, haystack, term).ratio() >= threshold:
                return True
        return False

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
    return client, search_documents, tools


@app.cell
def _():
    MAX_FUNCTION_CALLS = 5
    return (MAX_FUNCTION_CALLS,)


@app.cell
def _(MAX_FUNCTION_CALLS, client, copy, json, rprint, search_documents, tools):
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
    return (gen_multi_hop_gpt4,)


@app.cell
def _(MAX_FUNCTION_CALLS, client, copy, json, rprint, search_documents, tools):
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
    あなたは優秀な情報検索者です。

    与えられたツールを使って情報を検索しユーザの質問に答えてください。
    検索された情報に不足があれば、再度検索を行っても構いません。
    """

        USER_PROMPT = """
    NTT docomoのアンギラの国際通話の料金を教えてください。
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
