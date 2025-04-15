import os
import sys

import keyring

from dsegen.core import generate_english_paper


def configure_api():
    api_key = input("Enter your OpenRouter API key: ")
    default_model = input("Enter your default model: ")

    keyring.set_password("dsegen", "openrouter_api_key", api_key)
    keyring.set_password("dsegen", "openrouter_default_model", default_model)

    os.environ["OPENROUTER_API_KEY"] = api_key
    os.environ["OPENROUTER_DEFAULT_MODEL"] = default_model

    print("API credentials securely stored in system keyring")


def show_help():
    """Show help message for the CLI."""
    print("DSE Generator (dsegen) - Generate DSE practice papers")
    print("\nUsage:")
    print("  dsegen config               Configure API keys and default model")
    print("  dsegen english-speaking TOPIC FILE   Generate an English speaking paper")
    print("  dsegen english-speaking FILE.md FILE   Process existing markdown file")
    print("\nAliases:")
    print("  english-speaking: es")
    print("\nOptions:")
    print("  TOPIC                       The topic for the speaking paper")
    print("  FILE.md                     An existing markdown file to process")
    print("  FILE                        Output file path (.pdf, .md, or .html)")


def load_config():
    """Load configuration from the system keyring"""
    api_key = keyring.get_password("dsegen", "openrouter_api_key")
    default_model = keyring.get_password("dsegen", "openrouter_default_model")

    if api_key and default_model:
        os.environ["OPENROUTER_API_KEY"] = api_key
        os.environ["OPENROUTER_DEFAULT_MODEL"] = default_model
        return True
    return False


def main():

    if len(sys.argv) < 2:
        show_help()
        sys.exit(1)

    subcommand = sys.argv[1].lower()

    if subcommand == "config":
        configure_api()
        sys.exit(0)
    elif subcommand in ("english-speaking", "es"):
        if not os.getenv("OPENROUTER_API_KEY") or not os.getenv("OPENROUTER_DEFAULT_MODEL"):
            if not load_config():
                print("API key not configured. Run 'dsegen config' first.")
                sys.exit(1)
        if len(sys.argv) < 4:
            print("Usage: dsegen english-speaking <topic or file.md> <output_file>")
            sys.exit(1)
        topic_or_file = sys.argv[2]
        output_file = sys.argv[3]
        generate_english_paper(topic_or_file, output_file)
    elif subcommand in ("-h", "--help", "help"):
        show_help()
    else:
        print(f"Unknown subcommand: {subcommand}")
        show_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
