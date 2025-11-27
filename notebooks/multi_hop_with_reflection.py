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
    ### systemプロンプトに処理フローを書いてマルチホップを行うパターン
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
def _():
    from openai import OpenAI
    from pydantic import BaseModel, Field
    from tools import search_documents_raw, tools

    client = OpenAI()

    class ReflectionResult(BaseModel):
        advice: str = Field(
            ...,
            description="評価がNGの場合、次のツール選択・実行で参考になるようなアドバイスを設定する",
        )
        is_completed: bool = Field(
            ...,
            description="ユーザの質問に対して正しく回答できているかの評価結果",
        )
    return ReflectionResult, client, search_documents_raw, tools


@app.cell
def _():
    MAX_REFLECTIONS = 5
    return (MAX_REFLECTIONS,)


@app.cell
def _(
    MAX_REFLECTIONS,
    ReflectionResult,
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
        for i in range(MAX_REFLECTIONS):
            rprint(f">>> Iteration {i + 1}/{MAX_REFLECTIONS}")
            # ツール実行
            response = client.responses.create(
                model=model,
                input=input,
                tools=tools,
                tool_choice="required", # tool実行を強制する
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

            # 関数呼び出しがなければエラー
            if not has_function_call:
                raise "no tool choice error"

            # ツール結果から回答を生成
            response = client.responses.create(
                model=model,
                input=input,
            )
            answer = response.output_text
            input += response.output

            # リフレクション
            input += [
                {
                    "role": "user",
                    "content": "「2. リフレクション」を行ってください"
                }         
            ]
            response = client.responses.parse(
                model=model,
                input=input,
                text_format=ReflectionResult,
            )
            input += response.output
            reflection_result = response.output_parsed
            rprint("### reflection_result")
            rprint(reflection_result)
            if reflection_result.is_completed:
                return answer

            # 次のループへ
            input += [
                {
                    "role": "user",
                    "content": "リフレクションのアドバイスを参考に、「1. ツールを選択・実行して回答を生成」をやり直してください"
                }
            ]

        # 最大試行回数に達した場合
        print(f"警告: 最大試行回数({MAX_REFLECTIONS})に達しました")
        return answer
    return (gen_multi_hop_gpt4,)


@app.cell
def _(
    MAX_REFLECTIONS,
    ReflectionResult,
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
        for i in range(MAX_REFLECTIONS):
            rprint(f">>> Iteration {i + 1}/{MAX_REFLECTIONS}")

            # ツール実行
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
                tool_choice="required", # tool実行を強制する
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

            # 関数呼び出しがなければエラー
            if not has_function_call:
                raise "no tool choice error"

            # ツール結果から回答を生成
            response = client.responses.create(
                model=model,
                reasoning={
                    "effort": effort
                },
                text={
                    "verbosity": verbosity
                },
                input=input,
            )
            answer = response.output_text
            input += response.output

            # リフレクション
            input += [
                {
                    "role": "user",
                    "content": "「2. リフレクション」を行ってください"
                }         
            ]
            response = client.responses.parse(
                model=model,
                reasoning={
                    "effort": effort
                },
                text={
                    "verbosity": verbosity
                },
                input=input,
                text_format=ReflectionResult,
            )
            input += response.output
            reflection_result = response.output_parsed
            rprint("### reflection_result")
            rprint(reflection_result)
            if reflection_result.is_completed:
                return answer

            # 次のループへ
            input += [
                {
                    "role": "user",
                    "content": "リフレクションのアドバイスを参考に、「1. ツールを選択・実行して回答を生成」をやり直してください"
                }
            ]


        # 最大試行回数に達した場合
        print(f"警告: 最大試行回数({MAX_REFLECTIONS})に達しました")
        return answer
    return (gen_multi_hop_gpt5,)


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
    あなたは優秀な情報検索エージェントです。
    ユーザの質問に対してドキュメントデータベースから検索を行い、回答を行います。
    内部知識は使わずにツールから取得した情報のみを使って答えるようにしてください。

    以下のステップを交互に実行してユーザの質問に対して回答を行ってください。


    ### 1. ツールを実行して回答を生成
    ユーザの質問に対して必要なツールの実行を行い、その結果に基づいて回答を生成してください。
    回答出来なかった場合は、なぜ回答出来なかったか言語化してください。


    ### 2. リフレクション
    「1. ツールを実行して回答を生成」で生成された回答が、ユーザの質問に対して適切であるか評価します。

    評価がNGの場合、ツールの検索結果から新たに必要な検索キーワードがあれば、その旨をアドバイスに記載してください。
    アドバイスの内容をもとに「1. ツールを選択・実行して回答を生成」からやり直します。

    評価がOKの場合は、回答を終了します。
    """

        USER_PROMPT = """
    以下のユーザの質問に対して「1. ツールを選択・実行して回答を生成」を行なってください。


    ### ユーザの質問

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
            output = gen_multi_hop_gpt4(input, model)
            rprint({
                "model": model,
                "output": output,
            })

        # # 網羅的な組み合わせを生成
        combinations = list(product(GPT5_MODELS, GPT5_REASONING_EFFORTS, GPT5_TEXT_VERBOSITIES))

        # 結果を表示
        for i, (model, effort, verbosity) in enumerate(combinations, 1):
            print(f"### {model} effort: {effort} verbosity: {verbosity} ###")
            output = gen_multi_hop_gpt5(input, model, effort, verbosity)
            rprint({
                "model": model,
                "output": output,
                "effort": effort,
                "verbosity": verbosity,
            })

    _()
    return


if __name__ == "__main__":
    app.run()
