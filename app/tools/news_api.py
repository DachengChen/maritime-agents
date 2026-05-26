def get_latest_news(requirement: str) -> list[dict]:
    """Mock maritime news tool.

    TODO: Integrate a real maritime news API provider.
    """
    return [
        {
            "headline": f"Shipping market update related to: {requirement}",
            "summary": "Container freight rates remained stable this week across major routes.",
        },
        {
            "headline": "Regional port congestion watch",
            "summary": "Moderate delays reported in two transshipment hubs due to weather.",
        },
    ]
