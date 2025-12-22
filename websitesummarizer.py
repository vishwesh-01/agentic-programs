from bs4 import BeautifulSoup
import requests
from openai import OpenAI

# Standard headers to fetch a website
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}


def fetch_website_contents(url):
    """
    Return the title and contents of the website at the given url;
    truncate to 2,000 characters as a sensible limit
    """
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    title = soup.title.string if soup.title else "No title found"
    if soup.body:
        for irrelevant in soup.body(["script", "style", "img", "input"]):
            irrelevant.decompose()
        text = soup.body.get_text(separator="\n", strip=True)
    else:
        text = ""
    return (title + "\n\n" + text)[:2_000]


def summarize_website(url):
    webcontent = fetch_website_contents(url)

    system_prompt = """
    You are a snarky assistant that analyzes the contents of a website,
    and provides a short, snarky, humorous summary, ignoring text that might be navigation related.
    Respond in markdown. Do not wrap the markdown in a code block - respond just with the markdown.
    """

    user_prompt_prefix = """
    Here are the contents of a website.
    Provide a short summary of this website.
    If it includes news or announcements, then summarize these too.
    """

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"{user_prompt_prefix}\n\n{webcontent}"}]


    # using ollama
    OLLAMA_BASE_URL = "http://localhost:11434/v1"
    ollama = OpenAI(base_url=OLLAMA_BASE_URL, api_key='ollama')

    response = ollama.chat.completions.create(model="llama3.2", messages=messages)
    print(response.choices[0].message.content)

    # using openai
    # openai = OpenAI(api_key='your-openai-api-key-here')
    # response = openai.chat.completions.create(model="gpt-4.1-nano", messages=messages)
    # response.choices[0].message.content

url = str(input("Enter website URL to summarize: "))
summarize_website(url)