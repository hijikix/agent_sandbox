import marimo

__generated_with = "0.17.7"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    from itertools import product
    from rich import print as rprint
    return mo, product, rprint


@app.cell
def _():
    from dotenv import load_dotenv

    load_dotenv()
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### 色々なパターンでプランニングを行ってみます
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
        # 'high',
    ]

    GPT5_TEXT_VERBOSITIES = [
        'low',
        # 'medium',
        # 'high',
    ]
    return GPT5_MODELS, GPT5_REASONING_EFFORTS, GPT5_TEXT_VERBOSITIES


@app.cell
def _():
    from openai import OpenAI
    from pydantic import BaseModel

    client = OpenAI()

    class Plan(BaseModel):
        """レスポンスの型"""
        tasks: list[str]
    return Plan, client


@app.cell
def _(Plan, client):
    def gen_plan_gpt4(input, model) -> Plan:
        """gpt4系のapiコール"""
        response = client.responses.parse(
            model=model,
            input=input,
            text_format=Plan,
        )
        plan = response.output_parsed
        return plan
    return (gen_plan_gpt4,)


@app.cell
def _(Plan, client):
    def gen_plan_gpt5(input, model, effort, verbosity) -> Plan:
        """gpt5系のapiコール"""
        response = client.responses.parse(
            model=model,
            reasoning={
                "effort": effort
            },
            text={
                "verbosity": verbosity
            },
            input=input,
            text_format=Plan,
        )
        plan = response.output_parsed
        return plan
    return (gen_plan_gpt5,)


@app.cell
def _(mo):
    mo.md(r"""
    ### 情報検索タスクをプランニング（シンプルなシステムプロンプト）
    """)
    return


@app.cell
def _(
    GPT4_MODELS,
    GPT5_MODELS,
    GPT5_REASONING_EFFORTS,
    GPT5_TEXT_VERBOSITIES,
    gen_plan_gpt4,
    gen_plan_gpt5,
    product,
    rprint,
):
    def _():
        SYSTEM_PROMPT = """
    あなたは優秀な情報検索者です。

    ユーザの質問に対して情報取得タスクを作成してください。
    """
    
        USER_PROMPT = """
    ### ユーザの質問

    ドコモとソフトバンクの携帯電話の料金を比較してください。
    月のデータ使用量は30G程度です。
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
            plan = gen_plan_gpt4(input, model)
            rprint({
                "model": model,
                "plan": plan,
            })
    
        # 網羅的な組み合わせを生成
        combinations = list(product(GPT5_MODELS, GPT5_REASONING_EFFORTS, GPT5_TEXT_VERBOSITIES))
    
        # 結果を表示
        for i, (model, effort, verbosity) in enumerate(combinations, 1):
            plan = gen_plan_gpt5(input, model, effort, verbosity)
            rprint({
                "model": model,
                "effort": effort,
                "verbosity": verbosity,
                "plan": plan,
            })

    _()
    return


@app.cell
def _():
    ### 情報検索タスクをプランニング（色々考慮したシステムプロンプト）
    return


@app.cell
def _(
    GPT4_MODELS,
    GPT5_MODELS,
    GPT5_REASONING_EFFORTS,
    GPT5_TEXT_VERBOSITIES,
    gen_plan_gpt4,
    gen_plan_gpt5,
    product,
    rprint,
):
    def _():
        SYSTEM_PROMPT = """
    あなたは優秀な情報検索者です。

    ユーザの質問に対して情報取得タスクを作成してください。
    情報取得タスクは別のエージェントが実行し、それぞれ結果を返します。
    タスクの結果を全て参考にして最終的なユーザへの回答を作成します。

    ### 条件
    - それぞれの情報検索タスクは独立しているものとし、依存関係は無い様にする。
    - サブタスクは別のエージェントが実行する。
    - 出力は1行1タスクでシンプルな文章で、最大でも3行程度にまとめる。
    """
    
        USER_PROMPT = """
    ### ユーザの質問

    ドコモとソフトバンクの携帯電話の料金を比較してください。
    月のデータ使用量は30G程度です。
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
            plan = gen_plan_gpt4(input, model)
            rprint({
                "model": model,
                "plan": plan,
            })
    
        # 網羅的な組み合わせを生成
        combinations = list(product(GPT5_MODELS, GPT5_REASONING_EFFORTS, GPT5_TEXT_VERBOSITIES))
    
        # 結果を表示
        for i, (model, effort, verbosity) in enumerate(combinations, 1):
            plan = gen_plan_gpt5(input, model, effort, verbosity)
            rprint({
                "model": model,
                "effort": effort,
                "verbosity": verbosity,
                "plan": plan,
            })

    _()
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### 旅行計画タスクをプランニング
    """)
    return


@app.cell
def _(
    GPT4_MODELS,
    GPT5_MODELS,
    GPT5_REASONING_EFFORTS,
    GPT5_TEXT_VERBOSITIES,
    gen_plan_gpt4,
    gen_plan_gpt5,
    product,
    rprint,
):
    def _():
        input = [
            {
                "role": "developer",
                "content": "あなたは優秀な旅行プランナーです。"
            },
            {
                "role": "user",
                "content": "伊豆に旅行に行くための計画を立てたいです。プランニングのためのタスクを考えてください。"
            }
        ]
    
        for model in GPT4_MODELS:
            plan = gen_plan_gpt4(input, model)
            rprint({
                "model": model,
                "plan": plan,
            })
    
        # 網羅的な組み合わせを生成
        combinations = list(product(GPT5_MODELS, GPT5_REASONING_EFFORTS, GPT5_TEXT_VERBOSITIES))
    
        # 結果を表示
        for i, (model, effort, verbosity) in enumerate(combinations, 1):
            plan = gen_plan_gpt5(input, model, effort, verbosity)
            rprint({
                "model": model,
                "effort": effort,
                "verbosity": verbosity,
                "plan": plan,
            })

    _()
    return


if __name__ == "__main__":
    app.run()
