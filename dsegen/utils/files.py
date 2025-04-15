from playwright.async_api import async_playwright


async def html_to_pdf(html_content: str) -> bytes:
    """
    Convert HTML string to a one page A4 size PDF.
    """

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_content(html_content)

        pdf_byte = await page.pdf(
            format="A4",
            width="210mm",
            height="297mm",
            print_background=True,
        )
        await browser.close()
        return pdf_byte
