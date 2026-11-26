
from agent.generator import _fix_missing_spaces


test_cases = [
    "wherepersonalized learning helps students",
    "offeringa better learning experience",
    "suitable fora broad audience",
    "providinga useful solution",
    "designedfor the modern classroom",
]

print("\n========== SPACING FIX TEST ==========\n")

for original in test_cases:
    fixed = _fix_missing_spaces(original)

    print("Original:", original)
    print("Fixed:   ", fixed)
    print()
