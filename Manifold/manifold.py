import asyncio
import re
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async


def get_questions(status: str):
    jsonlist = []
    url = "https://api.manifold.markets/v0/search-markets?limit=1000&filter={}&offset={}"
    offset = 0
    while True:
        rurl = url.format(status, offset)
        response = requests.get(rurl).json()
        if not response:
            break
        jsonlist.extend(response)
        offset += 1000
    df = pd.DataFrame(jsonlist)
    exclude = ["STONK", "POLL", "BOUNTIED_QUESTION", "QUADRATIC_FUNDING", "NUMERIC"]
    df = df[~df["outcomeType"].isin(exclude)]
    includecols = ["id", "question", "url", "probability", "outcomeType", "uniqueBettorCount"]
    if status == "resolved":
        includecols.append("resolutionProbability")
    df = df[includecols]
    print("json done")
    return df


def get_text(id):
    url = f"https://api.manifold.markets/v0/market/{id}"
    temp = requests.get(url).json()
    if temp:
        if "textDescription" in temp:
            return temp["textDescription"]
    return None


async def pw_predict(p, url, type):
    if type == "BINARY":
        return None
    browser = await p.chromium.launch(headless=False)
    page = await browser.new_page()
    await stealth_async(page)
    await page.goto(url)
    print(f"{url} - {type}")
    if type in ["MULTIPLE_CHOICE", "FREE_RESPONSE"]:
        try:
            button = await page.get_by_role("button", name=r"show \d+ more answers").click()
        except:
            pass
        out1 = await page.locator("//div[@class='mx-[2px] mt-1 gap-2 flex flex-col']").evaluate("el => el.innerText")

        pattern = r"(\d+\.\d+%)\n(.*?)\n"
        matches = re.findall(pattern, out1)
        filtered_matches = [(percentage, name) for percentage, name in matches if percentage != "0%"]

        outdata = "\n".join([f"{percentage} - {name}" for percentage, name in filtered_matches])
        print(outdata)
    elif type in ["NUMBER", "PSEUDO_NUMERIC"]:
        try:
            button = await page.get_by_role("button", name=r"show \d+ more answers").click()
        except:
            pass
        out1 = await page.locator("//div[@class='items-baseline gap-2 text-3xl flex flex-row']").evaluate("el => el.innerText")
        return out1.replace("\n", "")
        print(out1)

    await browser.close()


async def pw_main(url, type):
    async with async_playwright() as playwright:
        await pw_predict(playwright, url, type)


def req_predict(url, type):
    if type == "BINARY":
        return None
    session = requests.session()
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
            "Authority": "pxidrgkatumlvfqaxcll.supabase.co",
            "Referer": "https://manifold.markets/",
            "Origin": "https://manifold.markets",
        }
    )
    x = session.get(url)
    for xpath in ["items-baseline gap-2 text-3xl flex flex-row", "flex items-baseline gap-2 text-2xl sm:text-3xl flex-row", "mx-[2px] mt-1 gap-2 flex flex-col"]:
        soup = BeautifulSoup(x.content, "lxml").find("div", attrs={"class": xpath})
        if soup:
            if type in ["NUMBER", "PSEUDO_NUMERIC"]:
                out = soup.text
            else:
                soup = soup.find_all("span")
                soup = list(filter(None, [i.text for i in soup]))[::-1]
                if len(soup) % 2 == 0:
                    out = [(x := f"{soup[i]} - {soup[i+1]}") for i in range(0, len(soup), 2) if "0.0%" not in f"{soup[i]} - {soup[i+1]}"]
                else:
                    if soup[-1] == "100%":
                        soup.pop(-1)
                        soup = [soup[i : i + 2] for i in range(0, len(soup), 2) if soup[i + 1] != "0.0%"]
                        soup = [item for sublist in soup for item in sublist]
                        out = [(x := f"{soup[i]} - {soup[i+1]}") for i in range(0, len(soup), 2) if "0.0%" not in f"{soup[i]} - {soup[i+1]}"]
                    else:
                        out = soup
                break
        else:
            out = None
    if not out:
        xpath = "w-full gap-3 lg:gap-4 flex flex-col"
        soup = BeautifulSoup(x.content, "lxml").find("div", attrs={"class": xpath})
        if soup:
            soup = soup.find_all("div", attrs={"class": "bg-canvas-50 w-full rounded flex flex-col"})
            out = [i.text.replace("100%", "").replace("%", "% ") for i in soup]
    session.close()
    return out


def req_main(url, type):
    for attempt in range(5):
        try:
            return req_predict(url, type)
        except:
            time.sleep(2**attempt)
    return None


def scrape(status: str):
    df = get_questions(status)
    df["text"] = df["id"].apply(get_text)
    # df['pred'] = df.apply(lambda x: req_main(x['url'], x['outcomeType']), axis=1)
    return df
