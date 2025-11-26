import marimo

__generated_with = "0.17.8"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import copy
    import json
    from itertools import product
    from rich import print as rprint
    return (rprint,)


@app.cell
def _(rprint):
    from openai import OpenAI
    client = OpenAI()

    response = client.responses.create(
        model="gpt-5",
        tools=[{"type": "web_search"}],
        input="What was a positive news story from today?"
    )

    rprint(response)
    print(response.output_text)
    return


if __name__ == "__main__":
    app.run()
