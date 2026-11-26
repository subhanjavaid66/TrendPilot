
from agent.planner import create_plan

try:
    plan = create_plan(
        topic="Artificial Intelligence",
        platform="Instagram",
        tone="Professional",
        output_type="Social Media Post"
    )

    print("\n========== TRENDPILOT PLAN ==========")
    print("Topic:", plan["topic"])
    print("Platform:", plan["platform"])
    print("Tone:", plan["tone"])
    print("Output Type:", plan["output_type"])

    print("\nPlanned Steps:")

    for index, step in enumerate(plan["steps"], start=1):
        print(f"{index}. Tool: {step['tool']}")
        print(f"   Purpose: {step['purpose']}")

except Exception as error:
    print("\nPlanner Error:", error)
