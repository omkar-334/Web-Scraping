import asyncio
from typing import List

from browser_use import Agent, Browser, BrowserConfig, Controller
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

load_dotenv()
DOWNLOAD_PROMPT = "You are given a website which has tabular data. Your task is to analyze the website and identify if it has any download/export option for the tabular data. If it has, then you need to provide the steps to download the data. You have to return either the download link or the download element locators. If download links are available, click on them and return the link address"


#  3 options
# <table> table
# <div> / <section> table
#  export as csv
# navigation/scrolling
# start manually, define each step(time)
# same filter latest function


# schema = {
#     "Country": "string",
#     "Most Recent Year": "integer",
#     "Most Recent Value": "float",
# }


url = "https://data.worldbank.org/indicator/EG.ELC.ACCS.ZS?name_desc=false"

# task1 = """Your task is to analyze the given URL to identify and extract all tabular data present on the webpage. Follow these steps carefully:

# 1. **Detect Tables:**
#    - Scan the entire webpage, including sections that require scrolling, to identify all tables.

# 2. **Extract Table Details:**
#    - For each detected table, retrieve its **title** as it is displayed on the webpage.
#    - Do not add any comments like 'extracted data', 'table data', etc.
#    - Extract the **column names** from the table header or equivalent elements.
# """

task1 = "You are given a website which has tabular data. Your task is to analyze the website and identify if it has any download/export option for the tabular data. If it has, then you need to provide the steps to download the data. You have to return either the download link or the download element locators. If download links are available, click on them and return the link address"


# class Table(BaseModel):
#     title: str
#     columns: List[str]


# controller = Controller(output_model=Table)


async def generate_locators(url):
    # browser = Browser()

    config = BrowserConfig(headless=True, disable_security=True)

    browser = Browser(config=config)
    llm = ChatOpenAI(model="gpt-4o")
    actions = [{"open_tab": {"url": url}}]

    # async with await browser.new_context() as context:
    agent = Agent(
        task=task1,
        llm=llm,
        browser=browser,
        # browser_context=context,
        initial_actions=actions,
        # controller=controller,
        save_conversation_path="logs/download",
    )
    history = await agent.run()
    result = history.final_result()
    print(result)

    await browser.close()


asyncio.run(generate_locators(url))
# Shift + Alt + F
