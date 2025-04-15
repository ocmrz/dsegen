import asyncio
import base64
import importlib.resources
import os
import sys
from functools import reduce
from pathlib import Path
from typing import Any, Callable, Iterable, Literal

import jinja2
import markdown
import openai
from openai.types.chat import ChatCompletionMessageParam

from dsegen.utils.files import html_to_pdf

Markdown = str
HTML = str


def prompt(topic: str) -> Iterable[ChatCompletionMessageParam]:
    """
    Generate few-shot prompt for generating DSE English speaking paper.
    """

    prompt_md = importlib.resources.files("dsegen.data").joinpath("prompt.md").read_text()
    unmanned_store = (
        importlib.resources.files("dsegen.data.examples").joinpath("unmanned-store.md").read_text()
    )
    night_owls = (
        importlib.resources.files("dsegen.data.examples").joinpath("night-owls.md").read_text()
    )

    return [
        {"role": "system", "content": prompt_md},
        {"role": "user", "content": "Topic: Japan culture Convenience stores"},
        {"role": "assistant", "content": unmanned_store},
        {"role": "user", "content": "Topic: Health Sleep patterns"},
        {"role": "assistant", "content": night_owls},
        {"role": "user", "content": f"Topic: {topic}"},
    ]


def generate_markdown(topic: str) -> Markdown:
    """
    Generate Markdown string for DSE English speaking paper in specified topic.
    """
    from dsegen.client import client

    try:
        print("Using model: ", os.getenv("OPENROUTER_DEFAULT_MODEL"))
        response = client.chat.completions.create(
            model=os.getenv("OPENROUTER_DEFAULT_MODEL"), messages=prompt(topic)
        )
        print(response)
        if not response.choices:
            raise openai.APIConnectionError(message=response.error, request=response)
        return response.choices[0].message.content
    except openai.APIConnectionError as e:
        print(f"Failed to connect to OpenRouter API: {e}")
        exit(1)
    except openai.RateLimitError as e:
        print(f"OpenRouter API request exceeded rate limit: {e}")
        exit(1)
    except openai.APIError as e:
        print(f"OpenRouter API returned an API Error: {e}")
        exit(1)


def markdown_to_html_from_template(markdown_content: Markdown) -> HTML:
    """
    Convert Markdown string to HTML string using Jinja template.
    """

    converted_html = markdown.markdown(markdown_content, extensions=["extra"])

    template_content = (
        importlib.resources.files("dsegen.data.templates").joinpath("template.html").read_text()
    )

    watermark_path = importlib.resources.files("dsegen.data.templates").joinpath("watermark.png")
    with open(watermark_path, "rb") as img_file:
        img_data = base64.b64encode(img_file.read()).decode("utf-8")

    watermark_data_url = f"data:image/png;base64,{img_data}"

    template: jinja2.Template = jinja2.Template(template_content)
    final_html_document = template.render(content=converted_html, watermark_data=watermark_data_url)

    return final_html_document


def pipe(data, *functions: Callable[[Any], Any]) -> Any:
    return reduce(lambda value, func: func(value), functions, data)


def render_markdown(markdown_string: str, output_format: Literal["pdf", "html"]) -> str:
    if output_format == "pdf":
        return html_to_pdf(markdown_to_html_from_template(markdown_string))
    elif output_format == "html":
        return markdown_to_html_from_template(markdown_string)


def process_markdown_file(input_file: str, output_file: str) -> None:
    """
    Receive a Markdown path and generate PDF, HTML, or Markdown file based on `output_file`'s extension.
    """

    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found")
        sys.exit(1)

    if not output_file.lower().endswith((".pdf", ".md", ".html")):
        print(f"Unsupported output format: {Path(output_file).suffix}")
        sys.exit(1)

    try:
        markdown_content = Path(input_file).read_text()
        html_content = markdown_to_html_from_template(markdown_content)

        if output_file.lower().endswith(".pdf"):
            pdf_byte = asyncio.run(html_to_pdf(html_content))
            Path(output_file).write_bytes(pdf_byte)
        elif output_file.lower().endswith(".md"):
            Path(output_file).write_text(markdown_content)
        elif output_file.lower().endswith(".html"):
            Path(output_file).write_text(html_content)

        print(f"Markdown file processed and saved to {output_file}")
    except Exception as e:
        print(f"Error processing markdown file: {e}")
        sys.exit(1)


def generate_english_paper(topic: str, output_file: str):
    if os.path.exists(topic) and topic.lower().endswith(".md"):
        return process_markdown_file(topic, output_file)

    if not os.getenv("OPENROUTER_API_KEY") or not os.getenv("OPENROUTER_DEFAULT_MODEL"):
        print("API key or default model not set. Run 'dsegen config' first.")
        sys.exit(1)

    if not output_file.lower().endswith((".pdf", ".md", ".html")):
        print(f"Unsupported output format: {Path(output_file).suffix}")
        sys.exit(1)

    markdown_content = generate_markdown(topic)
    html_content = markdown_to_html_from_template(markdown_content)

    if output_file.lower().endswith(".pdf"):
        pdf_bytes = asyncio.run(html_to_pdf(html_content))
        Path(output_file).write_bytes(pdf_bytes)
    elif output_file.lower().endswith(".md"):
        Path(output_file).write_text(markdown_content)
    elif output_file.lower().endswith(".html"):
        Path(output_file).write_text(html_content)

    print(f"English speaking paper on '{topic}' generated and saved to {output_file}")
