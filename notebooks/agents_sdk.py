import marimo

__generated_with = "0.17.8"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    from agents import Agent, Runner
    from rich import print as rprint
    return Agent, Runner, mo


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
async def _(Agent, Runner):
    agent = Agent(name="Assistant", instructions="You are a helpful assistant")

    result = await Runner.run(agent, "Write a haiku about recursion in programming.")
    print(result.final_output)
    return


if __name__ == "__main__":
    app.run()
