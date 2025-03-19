# DSE Generator (dsegen)

A command-line tool for generating DSE practice papers using AI. The tool can generate papers from topics or convert existing Markdown files to formatted documents.

## Features

- Generate English speaking papers from topics
- Convert existing Markdown files to PDF, HTML, or MD formats
- Clean and professional formatting
- Easy configuration with OpenRouter API

## Installation

### Option 1: Install from GitHub with uv

```bash
uv tool install git+https://github.com/ocmrz/dsegen.git
```

### Option 2: Install from GitHub with pipx

```bash
pipx install git+https://github.com/ocmrz/dsegen.git
```

### Option 3: Manual Installation

```bash
git clone https://github.com/ocmrz/dsegen.git
cd dsegen
uv pip install -e .
```

## Setup with OpenRouter

1. **Create an OpenRouter Account**
   - Sign up at [OpenRouter](https://openrouter.ai/)
   - Create an API key from your [dashboard](https://openrouter.ai/settings/keys)

2. **Configure the API Key**
   ```bash
   dsegen config
   ```
   - Enter your OpenRouter API key when prompted
   - Enter your preferred model (e.g., `openai/gpt-4-turbo`, `anthropic/claude-3-opus`)

## Usage

### Generate an English Speaking Paper

```bash
dsegen english-speaking "Technology Impact" output.pdf
```

### Process an Existing Markdown File

```bash
dsegen english-speaking my-paper.md output.pdf
```

### Output Formats
The tool supports the following output formats:
- PDF (recommended for printing)
- HTML (for web viewing)
- Markdown (for further editing)

### Command Aliases

- `dsegen es` is a shorter alias for `dsegen english-speaking`

## Help

To see all available commands and options:

```bash
dsegen --help
```

## Requirements

- Python 3.8 or higher
- Internet connection for API calls (when generating papers from topics)
- OpenRouter API key
