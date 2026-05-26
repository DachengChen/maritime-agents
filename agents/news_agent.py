"""News Agent – fetches and summarises maritime news."""

from __future__ import annotations

import logging

from models.report_models import NewsAgentResult
from tools.news_api import fetch_maritime_news

logger = logging.getLogger(__name__)


def run_news_agent(
    query: str = "maritime shipping port weather",
    max_results: int = 10,
    api_key: str | None = None,
    api_url: str | None = None,
) -> NewsAgentResult:
    """Execute the News Agent and return structured results.

    Args:
        query:       Search query forwarded to the news provider.
        max_results: Maximum number of articles to retrieve.
        api_key:     News API key (falls back to mock data if not provided).
        api_url:     Base URL of the news provider.

    Returns:
        A :class:`~models.report_models.NewsAgentResult` containing fetched
        articles or an error description.
    """

    logger.info("NewsAgent: fetching maritime news (query=%r, max=%d)", query, max_results)

    try:
        articles = fetch_maritime_news(
            query=query,
            max_results=max_results,
            api_key=api_key,
            api_url=api_url,
        )
        logger.info("NewsAgent: retrieved %d articles", len(articles))
        return NewsAgentResult(success=True, articles=articles)

    except Exception as exc:  # noqa: BLE001
        logger.exception("NewsAgent: unexpected error")
        return NewsAgentResult(success=False, error=str(exc))
