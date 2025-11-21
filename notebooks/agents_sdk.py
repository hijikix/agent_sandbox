import marimo

__generated_with = "0.17.8"
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
async def _(Agent, Runner, function_tool, rprint):
    @function_tool
    def search_documents(keywords: str) -> list[str]:
        if '国別料金表3' in keywords:
            response = "アンギラの国際通話料金は9999円/1分です。"
        elif 'アンギラ' in keywords or "Angila" in keywords or "Angira" in keywords:
            response = "アンギラの国際通話料金は国別料金表3に記載されています。"
        else:
            response = "情報が見つかりませんでした。"

        print(">>> search_documents called")
        rprint({
            'keywords': keywords,
            "response": response
        })
        return [response]

    agent = Agent(
        name="Hello world",
        instructions="You are a helpful agent.",
        tools=[search_documents],
    )


    result = await Runner.run(agent, input="アンギラの国際通話の料金をドキュメントデータベースから検索して教えてください")
    print(result.final_output)
    return


if __name__ == "__main__":
    app.run()
