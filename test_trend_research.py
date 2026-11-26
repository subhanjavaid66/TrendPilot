
from tools.trend_research import research_trends

try:

    result = research_trends("Artificial Intelligence")

    print("\n========== TREND RESEARCH RESULTS ==========")

    print("Topic:", result["topic"])
    print("Total Trends:", result["total_trends"])
    print("Research Date:", result["research_date"])
    print("Source:", result["source"])

    print("\nIdentified Trends:")

    for index, trend in enumerate(result["trends"], start=1):
        print(f"{index}. {trend}")

except Exception as error:
    print("Research Error:", error)
