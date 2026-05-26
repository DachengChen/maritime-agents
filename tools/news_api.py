"""Mock News API tool.

TODO: Replace the mock implementation with a real call to a News API provider
      (e.g. NewsAPI.org, GNews, Mediastack).  Set NEWS_API_KEY and NEWS_API_URL
      in your .env file and uncomment the httpx block below.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from models.maritime_models import NewsItem


def fetch_maritime_news(
    query: str = "maritime shipping port",
    max_results: int = 10,
    api_key: Optional[str] = None,
    api_url: Optional[str] = None,
) -> list[NewsItem]:
    """Return a list of recent maritime news articles.

    Currently returns mock data.  Replace the body of this function with a
    real API call when credentials are available::

        import httpx
        params = {
            "q": query,
            "apiKey": api_key,
            "language": "en",
            "pageSize": max_results,
        }
        response = httpx.get(f"{api_url}/everything", params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return [
            NewsItem(
                title=article["title"],
                source=article["source"]["name"],
                url=article["url"],
                summary=article.get("description"),
                published_at=datetime.fromisoformat(article["publishedAt"].rstrip("Z")),
            )
            for article in data.get("articles", [])
        ]
    """

    # ── MOCK DATA ──────────────────────────────────────────────────────────────
    mock_articles = [
        NewsItem(
            title="Suez Canal Traffic Surges as Vessel Backlogs Clear",
            source="Maritime Executive",
            url="https://example.com/news/1",
            summary=(
                "Transit numbers at the Suez Canal have returned to normal levels "
                "following last week's disruptions caused by adverse weather."
            ),
            published_at=datetime(2026, 5, 26, 6, 0, tzinfo=timezone.utc),
            keywords=["Suez Canal", "congestion", "weather"],
        ),
        NewsItem(
            title="Port of Rotterdam Announces 24-Hour Gate Extension",
            source="Port Technology",
            url="https://example.com/news/2",
            summary=(
                "Rotterdam will extend terminal gate hours to alleviate truck "
                "queuing reported over the past fortnight."
            ),
            published_at=datetime(2026, 5, 25, 14, 30, tzinfo=timezone.utc),
            keywords=["Rotterdam", "port", "gate hours"],
        ),
        NewsItem(
            title="Tropical Storm Alert Issued for Gulf of Mexico",
            source="NOAA Marine Forecasts",
            url="https://example.com/news/3",
            summary=(
                "A developing tropical system in the western Gulf is expected to "
                "intensify over the next 48 hours.  Vessels advised to monitor updates."
            ),
            published_at=datetime(2026, 5, 26, 8, 0, tzinfo=timezone.utc),
            keywords=["tropical storm", "Gulf of Mexico", "weather warning"],
        ),
        NewsItem(
            title="Fuel Price Update: Bunker Costs Rise 5% at Singapore",
            source="Bunkerworld",
            url="https://example.com/news/4",
            summary="VLSFO prices at the port of Singapore have risen by 5% week-on-week.",
            published_at=datetime(2026, 5, 25, 9, 0, tzinfo=timezone.utc),
            keywords=["bunker", "fuel", "Singapore"],
        ),
        NewsItem(
            title="New IMO Emission Regulations Take Effect in July",
            source="Lloyd's List",
            url="https://example.com/news/5",
            summary=(
                "Shipping companies are preparing for tighter carbon intensity "
                "requirements scheduled to come into force next month."
            ),
            published_at=datetime(2026, 5, 24, 12, 0, tzinfo=timezone.utc),
            keywords=["IMO", "emissions", "regulation"],
        ),
    ]

    return mock_articles[:max_results]
