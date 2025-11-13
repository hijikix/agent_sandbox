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
    GPT4_MODELS = [
        "gpt-4.1-2025-04-14",
    ]
    return (GPT4_MODELS,)


@app.cell
def _():
    GPT5_MODELS = [
        "gpt-5-nano-2025-08-07",
        # "gpt-5-mini-2025-08-07",
        # "gpt-5-2025-08-07",
    ]

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

    client = OpenAI()

    class Plan(BaseModel):
        tasks: list[str]

    return Plan, client


@app.cell
def _(Plan, client):
    def gen_travel_plan_gpt4(input, model) -> Plan:
        response = client.responses.parse(
            model=model,
            input=input,
            text_format=Plan,
        )
        plan = response.output_parsed
        return plan
    return (gen_travel_plan_gpt4,)


@app.cell
def _(Plan, client):
    def gen_travel_plan_gpt5(input, model, effort, verbosity) -> Plan:
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
    return (gen_travel_plan_gpt5,)


@app.cell
def _(
    GPT4_MODELS,
    GPT5_MODELS,
    GPT5_REASONING_EFFORTS,
    GPT5_TEXT_VERBOSITIES,
    gen_travel_plan_gpt4,
    gen_travel_plan_gpt5,
):
    from itertools import product
    from rich import print as rprint

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
        plan = gen_travel_plan_gpt4(input, model)
        rprint({
            "model": model,
            "plan": plan,
        })

    # 網羅的な組み合わせを生成
    combinations = list(product(GPT5_MODELS, GPT5_REASONING_EFFORTS, GPT5_TEXT_VERBOSITIES))

    # 結果を表示
    for i, (model, effort, verbosity) in enumerate(combinations, 1):
        plan = gen_travel_plan_gpt5(input, model, effort, verbosity)
        rprint({
            "model": model,
            "effort": effort,
            "verbosity": verbosity,
            "plan": plan,
        })
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
