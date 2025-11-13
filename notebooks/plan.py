import marimo

__generated_with = "0.17.7"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return


@app.cell
def _():
    from dotenv import load_dotenv

    load_dotenv()
    return


@app.cell
def _():
    from rich import print as rprint
    from openai import OpenAI
    from pydantic import BaseModel

    client = OpenAI()

    model="gpt-5-nano-2025-08-07"

    class Plan(BaseModel):
        tasks: list[str]

    response = client.responses.parse(
        model=model,
        reasoning={
            "effort": "low"
        },
        text={
            "verbosity": "low"
        },
        input=[
            {
                "role": "developer",
                "content": "あなたは優秀な旅行プランナーです。"
            },
            {
                "role": "user",
                "content": "伊豆に旅行に行くための計画を立てたいです。プランニングのためのタスクを考えてください。"
            }
        ],
        text_format=Plan,
    )

    plan = response.output_parsed

    rprint(plan)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
