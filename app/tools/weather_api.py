def get_weather_outlook(requirement: str) -> list[dict]:
    """Mock maritime weather data.

    TODO: Integrate a weather API with marine forecasts.
    """
    return [
        {"region": "South China Sea", "outlook": "High winds expected over 24h"},
        {"region": "North Atlantic", "outlook": "Calm to moderate conditions"},
    ]
