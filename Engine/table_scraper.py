import asyncio
from dataclasses import dataclass
from io import StringIO
from typing import TYPE_CHECKING

import pandas as pd
import playwright
from playwright.async_api import async_playwright

from args import create_args

if TYPE_CHECKING:
    import playwright.async_api


def get_loop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop


@dataclass
class Config:
    headless: bool = True
    text_only: bool = False
    schema: dict = None
    datetime_columns: bool = False
    datetime_columns_format: str = None


class TableScraper:
    def __init__(self, url, headless=False, text_only=False, schema: dict = None):
        self.args = create_args(headless, text_only)
        self.url = url
        self.schema = schema
        self.p: playwright.async_api.Playwright = None
        self.browser: playwright.async_api.Browser = None
        self.page: playwright.async_api.Page = None

    async def start(self):
        self.p = await async_playwright().start()
        self.browser = await self.p.chromium.launch(**self.args)
        self.page = await self.browser.new_page()
        await self.page.goto(self.url)

    @staticmethod
    def extract_table(table_html):
        try:
            df = pd.read_html(StringIO(table_html))[0]
        except ValueError:
            return None
        return df

    async def if_table_exists(self):
        tables = await self.page.locator("table").all()
        return tables if len(tables) > 0 else None

    async def extract_tables(self, tables, desired_table_index=None):
        for i, table in enumerate(tables):
            if desired_table_index is not None and i != desired_table_index:
                continue
            table_html = await table.evaluate("el => el.outerHTML")
            df = self.extract_table(table_html)
            df.to_excel(f"table_{i}.xlsx", index=False)

    async def main(self):
        await self.start()
