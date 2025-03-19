import os
import os
import sys
import asyncio
from pathlib import Path
from typing import TypeAlias, Iterable
from functools import reduce
import importlib.resources

import markdown
import jinja2
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from playwright.async_api import async_playwright

Markdown: TypeAlias = str
HTML: TypeAlias = str

client = OpenAI(api_key=os.getenv("OPENROUTER_API_KEY"), base_url="https://openrouter.ai/api/v1")


def prompt(topic: str) -> Iterable[ChatCompletionMessageParam]:
    prompt_md = importlib.resources.files('dsegen.data').joinpath('prompt.md').read_text()
    unmanned_store = importlib.resources.files('dsegen.data.examples').joinpath('unmanned-store.md').read_text()
    night_owls = importlib.resources.files('dsegen.data.examples').joinpath('night-owls.md').read_text()
    
    return [
        {"role": "system", "content": prompt_md},
        {"role": "user", "content": "Topic: Japan culture Convenience stores"},
        {"role": "assistant", "content": unmanned_store},
        {"role": "user", "content": "Topic: Health Sleep patterns"},
        {"role": "assistant", "content": night_owls},
        {"role": "user", "content": f"Topic: {topic}"},
    ]


def generate_markdown(topic: str) -> Markdown:
    response = client.chat.completions.create(
        model=os.getenv("OPENROUTER_DEFAULT_MODEL"), messages=prompt(topic)
    )
    return response.choices[0].message.content


def render_document(markdown_content: Markdown) -> HTML:
    converted_html = markdown.markdown(markdown_content, extensions=["extra"])
    template_content = importlib.resources.files('dsegen.data.templates').joinpath('template.html').read_text()
    template = jinja2.Template(template_content)
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


def configure_api():
    api_key = input("Enter your OpenRouter API key: ")
    default_model = input("Enter your default model: ")
    
    with open(".env", "w") as f:
        f.write(f"OPENROUTER_API_KEY={api_key}\n")
        f.write(f"OPENROUTER_DEFAULT_MODEL={default_model}\n")
    
    os.environ["OPENROUTER_API_KEY"] = api_key
    os.environ["OPENROUTER_DEFAULT_MODEL"] = default_model
    
    print("Configuration updated")


def generate_english_paper(topic, output_file):
    """Generate an English DSE speaking practice paper."""
    if not os.getenv("OPENROUTER_API_KEY") or not os.getenv("OPENROUTER_DEFAULT_MODEL"):
        print("API key or default model not set. Run 'dsegen config' first.")
        sys.exit(1)

    if not output_file.lower().endswith(('.pdf', '.md', '.html')):
        print(f"Unsupported output format: {Path(output_file).suffix}")
        sys.exit(1)

    markdown_content = generate_markdown(topic)
    html_content = render_document(markdown_content)

    if output_file.lower().endswith(".pdf"):
        asyncio.run(html_to_pdf(html_content, output_file))
    elif output_file.lower().endswith(".md"):
        Path(output_file).write_text(markdown_content)
    elif output_file.lower().endswith(".html"):
        Path(output_file).write_text(html_content)

    print(f"English speaking paper on '{topic}' generated and saved to {output_file}")


def show_help():
    """Show help message for the CLI."""
    print("DSE Generator (dsegen) - Generate DSE practice papers")
    print("\nUsage:")
    print("  dsegen config               Configure API keys and default model")
    print("  dsegen english-speaking TOPIC FILE   Generate an English speaking paper")
    print("\nAliases:")
    print("  english-speaking: es")
    print("\nOptions:")
    print("  TOPIC                       The topic for the speaking paper")
    print("  FILE                        Output file path (.pdf, .md, or .html)")


def main():
    if len(sys.argv) < 2:
        show_help()
        sys.exit(1)
    
    subcommand = sys.argv[1].lower()
    
    if subcommand == "config":
        configure_api()
        sys.exit(0)
    elif subcommand in ("english-speaking", "es"):
        if len(sys.argv) < 4:
            print("Usage: dsegen english-speaking <topic> <output_file>")
            sys.exit(1)
        topic = sys.argv[2]
        output_file = sys.argv[3]
        generate_english_paper(topic, output_file)
    elif subcommand in ("-h", "--help", "help"):
        show_help()
    else:
        print(f"Unknown subcommand: {subcommand}")
        show_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
