FROM mcr.microsoft.com/playwright/python:v1.51.0-jammy 
RUN pip install uv
WORKDIR /app
COPY pyproject.toml uv.lock /app/
COPY dsegen /app/dsegen
RUN uv sync --frozen --no-cache --extra server
EXPOSE 8080
CMD ["uv", "run", "uvicorn", "dsegen.server:app", "--host", "0.0.0.0", "--port", "8080"]
