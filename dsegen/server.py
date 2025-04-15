import asyncio
from typing import Awaitable, Callable, Dict, Literal, TypeVar, Union

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

from dsegen.core import generate_markdown, markdown_to_html_from_template
from dsegen.utils.files import html_to_pdf

T = TypeVar("T")
Content = str
OutputProcessor = Callable[[Content], Union[str, Awaitable[bytes]]]

app = FastAPI(
    title="DSE Generator API", description="API for generating DSE practice papers", version="0.1.0"
)


class GenerateEnglishSpeakingRequest(BaseModel):
    format: Literal["markdown", "html", "plain"]
    content: str

    class Config:
        schema_extra = {"example": {"format": "plain", "content": "Hong Kong Tourism Industry"}}


@app.get("/")
async def root():
    return {"status": "ok"}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/v1/generate/english-speaking")
async def generate(
    request: GenerateEnglishSpeakingRequest,
    output: Literal["markdown", "pdf", "html"] = Query(
        default="pdf", description="Output format for the generated paper"
    ),
):
    """
    Generate an English speaking paper in the specified output format.

    - Input formats:
      - plain: Plain text topic to generate a paper about
      - markdown: Pre-written paper in markdown format
      - html: Pre-formatted HTML content

    - Output formats:
      - markdown: Returns JSON with markdown content
      - html: Returns HTML document
      - pdf: Returns PDF document
    """

    input_processors: Dict[str, Callable[[str], str]] = {
        "plain": generate_markdown,
        "markdown": lambda x: x,
        "html": markdown_to_html_from_template,
    }

    output_processors = {
        "markdown": {
            "processor": lambda x: x,
            "media_type": "application/json",
            "transform": lambda x: {"content": x},
        },
        "html": {
            "processor": markdown_to_html_from_template,
            "media_type": "text/html",
            "transform": lambda x: x,
        },
        "pdf": {
            "processor": lambda x: html_to_pdf(markdown_to_html_from_template(x)),
            "media_type": "application/pdf",
            "transform": lambda x: x,
            "headers": {"Content-Disposition": "attachment; filename=speaking_paper.pdf"},
        },
    }

    try:
        if request.format not in input_processors:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported input format: {request.format}. Supported formats: {', '.join(input_processors.keys())}",
            )

        markdown_content = input_processors[request.format](request.content)
        output_config = output_processors[output]
        result = output_config["processor"](markdown_content)

        if asyncio.iscoroutine(result):
            result = await result

        content = output_config["transform"](result)

        response_kwargs = {"content": content, "media_type": output_config["media_type"]}

        if "headers" in output_config:
            response_kwargs["headers"] = output_config["headers"]

        return (
            JSONResponse(**response_kwargs) if output == "markdown" else Response(**response_kwargs)
        )

    except HTTPException:
        raise
    except Exception as e:
        import traceback

        print(f"Error generating content: {str(e)}")
        print(traceback.format_exc())

        raise HTTPException(status_code=500, detail=f"Error generating content: {str(e)}")
