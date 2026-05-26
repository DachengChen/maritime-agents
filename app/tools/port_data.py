def get_port_status(requirement: str) -> list[dict]:
    """Mock port intelligence data.

    TODO: Integrate with real port operation data feeds.
    """
    return [
        {"port": "Singapore", "congestion_level": "medium", "note": "Berth waiting time +6h"},
        {"port": "Rotterdam", "congestion_level": "low", "note": "Normal operations"},
    ]
