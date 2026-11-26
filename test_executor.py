
from agent.planner import create_plan
from agent.executor import execute_plan

try:

    # Generate an AI plan
    plan = create_plan(
        topic="Artificial Intelligence",
        platform="Instagram",
        tone="Professional",
        output_type="Social Media Post"
    )

    print("\n========== AI PLAN GENERATED ==========")

    # Execute the planned tools
    results = execute_plan(plan)

    print("\n========== TOOL EXECUTION RESULTS ==========")

    for tool_name, result in results.items():

        print(f"\n{tool_name.upper()}")
        print("-" * 40)

        for key, value in result.items():
            print(f"{key}: {value}")

except Exception as error:

    print("\nExecution Error:", error)
