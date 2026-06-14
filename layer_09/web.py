# layer_09/web.py
import httpx
from bs4 import BeautifulSoup
import json
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; AgentHarness/1.0)"
}

MAX_CONTENT_LENGTH = 4000  # chars — keep responses token-friendly


def fetch_url(url: str) -> str:
    """Fetch a URL and return clean readable text (no HTML tags)."""
    try:
        with httpx.Client(follow_redirects=True, timeout=15) as client:
            resp = client.get(url, headers=HEADERS)
            resp.raise_for_status()
            content_type = resp.headers.get("content-type", "")

            # Return raw text for non-HTML content
            if "html" not in content_type:
                return resp.text[:MAX_CONTENT_LENGTH]

            soup = BeautifulSoup(resp.text, "html.parser")

            # Remove noise
            for tag in soup(["script", "style", "nav", "footer",
                              "header", "aside", "form", "iframe"]):
                tag.decompose()

            # Extract readable text
            text = soup.get_text(separator="\n")

            # Clean up excessive whitespace
            lines = [line.strip() for line in text.splitlines()]
            lines = [l for l in lines if l]
            clean = "\n".join(lines)

            return clean[:MAX_CONTENT_LENGTH]

    except httpx.TimeoutException:
        return "Error: request timed out"
    except httpx.HTTPStatusError as e:
        return f"Error: HTTP {e.response.status_code}"
    except Exception as e:
        return f"Error fetching URL: {e}"


def web_search(query: str, max_results: int = 5) -> str:
    """
    Search the web via DuckDuckGo's HTML interface.
    No API key required.
    """
    try:
        url = "https://html.duckduckgo.com/html/"
        with httpx.Client(follow_redirects=True, timeout=15) as client:
            resp = client.post(
                url,
                data={"q": query},
                headers={**HEADERS, "Content-Type": "application/x-www-form-urlencoded"},
            )
            resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        results = []

        for result in soup.select(".result")[:max_results]:
            title_el = result.select_one(".result__title")
            snippet_el = result.select_one(".result__snippet")
            link_el = result.select_one(".result__url")

            title = title_el.get_text(strip=True) if title_el else "No title"
            snippet = snippet_el.get_text(strip=True) if snippet_el else "No snippet"
            link = link_el.get_text(strip=True) if link_el else ""

            results.append({
                "title": title,
                "url": link,
                "snippet": snippet,
            })

        if not results:
            return "No results found."

        # Format as readable text
        lines = []
        for i, r in enumerate(results, 1):
            lines.append(f"{i}. {r['title']}")
            lines.append(f"   {r['url']}")
            lines.append(f"   {r['snippet']}")
            lines.append("")

        return "\n".join(lines)

    except Exception as e:
        return f"Error searching: {e}"