
import requests
import xml.etree.ElementTree as ET

from langchain_core.tools import tool


# Step 1: Search arXiv

def search_arxiv_papers(
    topic: str,
    max_results: int = 5,
) -> str:
    """Fetch recent research papers from the arXiv API."""

    terms = topic.lower().split()
    query = " AND ".join(f"all:{term}" for term in terms)

    url = "https://export.arxiv.org/api/query"

    params = {
        "search_query": query,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }

    print(f"Searching arXiv for: {topic}")

    response = requests.get(
        url,
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    print("Status code:", response.status_code)
    print("Status text:", response.reason)

    return response.text


# Step 2: Parse the arXiv XML response

def parse_arxiv_xml(xml_content: str) -> dict:
    """Convert arXiv XML into structured paper metadata."""

    namespaces = {
        "atom": "http://www.w3.org/2005/Atom",
        "arxiv": "http://arxiv.org/schemas/atom",
    }

    root = ET.fromstring(xml_content)
    entries = []

    for entry in root.findall("atom:entry", namespaces):

        title = (
            entry.findtext("atom:title", namespaces=namespaces) or ""
        ).strip()

        summary = (
            entry.findtext("atom:summary", namespaces=namespaces) or ""
        ).strip()

        authors = [
            author.findtext("atom:name", namespaces=namespaces)
            for author in entry.findall("atom:author", namespaces)
        ]

        categories = [
            category.attrib.get("term")
            for category in entry.findall("atom:category", namespaces)
        ]

        published = entry.findtext(
            "atom:published", namespaces=namespaces
        )

        paper_id = (
            entry.findtext("atom:id", namespaces=namespaces) or ""
        ).strip()

        pdf_url = None

        for link in entry.findall("atom:link", namespaces):
            if (
                link.attrib.get("title") == "pdf"
                or link.attrib.get("type") == "application/pdf"
            ):
                pdf_url = link.attrib.get("href")
                break

        # Construct the standard PDF link if necessary.
        if pdf_url is None and paper_id:
            pdf_url = paper_id.replace(
                "http://arxiv.org/abs/",
                "https://arxiv.org/pdf/",
            ).replace(
                "https://arxiv.org/abs/",
                "https://arxiv.org/pdf/",
            )

        if title:
            entries.append({
                "title": title,
                "authors": authors,
                "summary": summary,
                "categories": categories,
                "published": published,
                "arxiv_url": paper_id,
                "pdf": pdf_url,
            })

    return {"entries": entries}


# Step 3: Create the LangChain tool

@tool
def arxiv_search(topic: str) -> list[dict]:
    """Search arXiv for recent research papers.

    Args:
        topic: The research topic to search for.

    Returns:
        A list of dictionaries containing paper titles, authors,
        summaries, categories, publication dates, and PDF links.
    """

    print("\nARXIV Agent called")
    print(f"Searching arXiv for papers about: {topic}")

    # Fetch XML and parse it into a dictionary.
    xml_content = search_arxiv_papers(
        topic=topic,
        max_results=5,
    )

    papers = parse_arxiv_xml(xml_content)
    entries = papers["entries"]

    if not entries:
        print(f"No papers found for topic: {topic}")
        return []

    print(f"Found {len(entries)} papers about {topic}")

    # Return the list itself, matching the tool's type annotation.
    return entries


# Step 4: Test this file independently

if __name__ == "__main__":

    results = arxiv_search.invoke({
        "topic": "machine learning quantum computing"
    })

    if results:
        for index, paper in enumerate(results, start=1):
            print(f"\n{'=' * 60}")
            print(f"Paper {index}: {paper['title']}")
            print(f"Authors: {', '.join(paper['authors'])}")
            print(f"Published: {paper['published']}")
            print(f"Summary: {paper['summary']}")
            print(f"arXiv: {paper['arxiv_url']}")
            print(f"PDF: {paper['pdf']}")
    else:
        print("No papers were returned by arXiv.")
