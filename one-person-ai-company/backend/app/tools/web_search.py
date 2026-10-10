"""
A minimal web-search tool the Research Agent can call.

Uses DuckDuckGo's HTML endpoint via `requests` so no API key is
required to get the project running. This is intentionally simple --
swap in a paid search API here later without touching agent code,
since agents only see the @tool-decorated function below.
"""
import requests

try:
    from crewai.tools import tool
except ImportError:  # crewai not installed in this environment
    def tool(name):
        def decorator(fn):
            return fn
        return decorator


@tool("web_search")
def web_search(query: str) -> str:
    """Search the web for a query and return a short list of results (title + snippet + url)."""
    try:
        resp = requests.get(
            "https://html.duckduckgo.com/html/",
            params={"q": query},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10,
        )
        resp.raise_for_status()
    except Exception as exc:  # noqa: BLE001
        return f"Web search failed: {exc}"

    # Very small, dependency-free scrape of DuckDuckGo's HTML result markup.
    import re

    results = re.findall(
        r'result__a" href="(.*?)".*?>(.*?)</a>.*?result__snippet.*?>(.*?)</a>',
        resp.text,
        re.DOTALL,
    )
    if not results:
        return "No results found."

    lines = []
    for url, title, snippet in results[:5]:
        clean_title = re.sub("<.*?>", "", title)
        clean_snippet = re.sub("<.*?>", "", snippet)
        lines.append(f"- {clean_title}: {clean_snippet} ({url})")
    return "\n".join(lines)
