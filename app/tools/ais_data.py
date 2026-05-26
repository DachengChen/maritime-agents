def get_vessel_movements(requirement: str) -> list[dict]:
    """Mock AIS vessel movement data.

    TODO: Integrate a real AIS provider.
    """
    return [
        {"vessel": "MV Ocean Star", "status": "Underway", "eta": "2026-05-27T08:30:00Z"},
        {"vessel": "MV Blue Horizon", "status": "At Port", "eta": "2026-05-28T11:15:00Z"},
    ]
