from app.tools.ais_data import get_vessel_movements
from app.tools.news_api import get_latest_news
from app.tools.port_data import get_port_status
from app.tools.weather_api import get_weather_outlook


class MaritimeReportAgent:
    def _select_sources(self, requirement_text: str) -> set[str]:
        text = requirement_text.lower()
        sources: set[str] = set()

        if any(keyword in text for keyword in ["vessel", "ship", "ais", "fleet"]):
            sources.add("ais")
        if any(keyword in text for keyword in ["port", "terminal", "congestion"]):
            sources.add("port")
        if any(keyword in text for keyword in ["weather", "storm", "wind"]):
            sources.add("weather")
        if any(keyword in text for keyword in ["news", "market", "trade", "freight"]):
            sources.add("news")

        return sources or {"ais", "port", "weather", "news"}

    def generate_report(self, requirement_text: str, language: str = "en") -> str:
        sources = self._select_sources(requirement_text)

        sections: list[str] = [
            "# Maritime Intelligence Report",
            "",
            f"- Preferred language: {language}",
            f"- Monitoring requirement: {requirement_text}",
            "",
            "## Summary",
            "This report was generated from mock maritime intelligence data sources.",
            "",
        ]

        if "news" in sources:
            sections.append("## Maritime News Signals")
            for item in get_latest_news(requirement_text):
                sections.append(f"- **{item['headline']}**: {item['summary']}")
            sections.append("")

        if "ais" in sources:
            sections.append("## Vessel Movements (AIS)")
            for item in get_vessel_movements(requirement_text):
                sections.append(
                    f"- {item['vessel']}: {item['status']}, ETA {item['eta']}"
                )
            sections.append("")

        if "port" in sources:
            sections.append("## Port Operations")
            for item in get_port_status(requirement_text):
                sections.append(
                    f"- {item['port']}: congestion={item['congestion_level']} ({item['note']})"
                )
            sections.append("")

        if "weather" in sources:
            sections.append("## Weather Outlook")
            for item in get_weather_outlook(requirement_text):
                sections.append(f"- {item['region']}: {item['outlook']}")
            sections.append("")

        sections.append("## Suggested Actions")
        sections.append("- Review risk exposure and route alternatives for impacted regions.")
        sections.append("- Confirm vessel and port operation assumptions with current ops data.")

        return "\n".join(sections)


report_agent = MaritimeReportAgent()
