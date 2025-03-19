import os
from pathlib import Path
from typing import TypeAlias, Iterable
import asyncio
import markdown
import jinja2
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from functools import reduce
import sys
from playwright.async_api import async_playwright

Markdown: TypeAlias = str
HTML: TypeAlias = str

client = OpenAI(api_key=os.getenv("OPENROUTER_API_KEY"), base_url="https://openrouter.ai/api/v1")


def prompt(topic: str) -> Iterable[ChatCompletionMessageParam]:
    return [
        {"role": "system", "content": Path("prompt.md").read_text()},
        {"role": "user", "content": "Topic: Japan culture Convenience stores"},
        {"role": "assistant", "content": Path("examples/unmanned-store.md").read_text()},
        {"role": "user", "content": "Topic: Health Sleep patterns"},
        {"role": "assistant", "content": Path("examples/night-owls.md").read_text()},
        {"role": "user", "content": f"Topic: {topic}"},
    ]


def generate_markdown(topic: str) -> Markdown:
    response = client.chat.completions.create(
        model=os.getenv("OPENROUTER_DEFAULT_MODEL"), messages=prompt(topic)
    )
    return response.choices[0].message.content


def render_document(markdown_content: Markdown) -> HTML:
    converted_html = markdown.markdown(markdown_content, extensions=["extra"])
    template = jinja2.Template(Path("templates/template.html").read_text())
    final_html_document = template.render(content=converted_html)
    return final_html_document


async def html_to_pdf(html_content: str, output_file: str) -> None:
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_content(html_content)
        await page.pdf(
            path=output_file, format="A4", width="210mm", height="297mm", print_background=True
        )
        await browser.close()


def pipe(data, *functions):
    return reduce(lambda value, func: func(value), functions, data)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python main.py <topic> <output_file>")
        sys.exit(1)

    assert os.getenv("OPENROUTER_API_KEY") is not None, "OPENROUTER_API_KEY is not set"
    assert os.getenv("OPENROUTER_DEFAULT_MODEL") is not None, "OPENROUTER_DEFAULT_MODEL is not set"

    topic = sys.argv[1]
    output_file = sys.argv[2]

    result = pipe(topic, generate_markdown, render_document)

    if output_file.lower().endswith(".pdf"):
        asyncio.run(html_to_pdf(result, output_file))
    else:
        Path(output_file).write_text(result)

    print(f"Paper on '{topic}' generated and saved to {output_file}")
