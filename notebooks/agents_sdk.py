import marimo

__generated_with = "0.18.1"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    from agents import Agent, Runner
    from agents.model_settings import ModelSettings
    from rich import print as rprint
    from itertools import product
    return Agent, ModelSettings, Runner, mo, product, rprint


@app.cell
def _():
    from dotenv import load_dotenv

    load_dotenv()
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### agents_sdkによる実装
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
        "minimal",
        # 'low',
        # "medium",
        "high",
    ]

    GPT5_TEXT_VERBOSITIES = [
        "low",
        # "medium",
        "high",
    ]
    return GPT5_MODELS, GPT5_REASONING_EFFORTS, GPT5_TEXT_VERBOSITIES


@app.cell
def _():
    from tools import search_documents

    INSTARUCTIONS = """
    あなたは優秀な検索エージェントです。

    与えられたツールを使って情報を検索しユーザの質問に答えてください。
    内部知識は使わずにツールから取得した情報のみを使って答えるようにしてください。

    検索された情報に不足があれば、再度検索を行っても構いません。
    """
    return INSTARUCTIONS, search_documents


@app.cell
def _(Agent, INSTARUCTIONS, Runner, search_documents):
    async def gen_gpt4(input: str, model: str):
        agent = Agent(
            name="検索エージェント",
            instructions=INSTARUCTIONS,
            tools=[search_documents],
            model=model,
        )

        result = await Runner.run(agent, input=input)
        return result.final_output
    return (gen_gpt4,)


@app.cell
def _(Agent, INSTARUCTIONS, ModelSettings, Runner, search_documents):
    async def gen_gpt5(input: str, model: str, effort: str, verbosity: str):
        agent = Agent(
            name="検索エージェント",
            instructions=INSTARUCTIONS,
            tools=[search_documents],
            model=model,
            model_settings=ModelSettings(
                effort=effort,
                verbosity=verbosity,
            ),
        )

        result = await Runner.run(agent, input=input)
        return result.final_output
    return (gen_gpt5,)


@app.cell
async def _(
    GPT4_MODELS,
    GPT5_MODELS,
    GPT5_REASONING_EFFORTS,
    GPT5_TEXT_VERBOSITIES,
    gen_gpt4,
    gen_gpt5,
    product,
    rprint,
):
    async def _():
        input = "ネクサス3000に搭載されているCPUの製造元の本社所在地は？"

        for model in GPT4_MODELS:
            print(f"### {model} ###")
            final_output = await gen_gpt4(input, model)
            rprint(
                {
                    "model": model,
                    "final_output": final_output,
                }
            )

        # # 網羅的な組み合わせを生成
        combinations = list(
            product(GPT5_MODELS, GPT5_REASONING_EFFORTS, GPT5_TEXT_VERBOSITIES)
        )

        # 結果を表示
        for i, (model, effort, verbosity) in enumerate(combinations, 1):
            print(f"### {model} effort: {effort} verbosity: {verbosity} ###")
            final_output = await gen_gpt5(input, model, effort, verbosity)
            rprint(
                {
                    "model": model,
                    "final_output": final_output,
                }
            )

    await _()
    return


if __name__ == "__main__":
    app.run()
