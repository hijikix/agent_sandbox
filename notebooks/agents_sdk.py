import marimo

__generated_with = "0.18.1"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    from agents import Agent, Runner, function_tool
    from rich import print as rprint
    return Agent, Runner, function_tool, mo, rprint


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
def _(function_tool, rprint):
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

    @function_tool
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
    return (search_documents,)


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
        # 'minimal',
        # 'low',
        "medium",
        # 'high',
    ]

    GPT5_TEXT_VERBOSITIES = [
        # 'low',
        "medium",
        # 'high',
    ]
    return (GPT5_MODELS,)


@app.cell
def _(Agent, Runner, search_documents):
    async def gen(input: str, model: str):
        INSTARUCTIONS = """
        あなたは優秀な検索エージェントです。

        与えられたツールを使って情報を検索しユーザの質問に答えてください。
        検索された情報に不足があれば、再度検索を行っても構いません。
        """

        agent = Agent(
            name="検索エージェント",
            instructions=INSTARUCTIONS,
            tools=[search_documents],
            model=model,
        )

        result = await Runner.run(agent, input=input)
        return result.final_output
    return (gen,)


@app.cell
async def _(GPT4_MODELS, GPT5_MODELS, gen, rprint):
    async def _():
        input = "アンギラの国際通話の料金を教えてください。"

        for model in GPT4_MODELS:
            final_output = await gen(input, model)
            rprint(
                {
                    "model": model,
                    "final_output": final_output,
                }
            )

        for model in GPT5_MODELS:
            final_output = await gen(input, model)
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
