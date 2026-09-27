from src.claude_agent import ask_claude


questions = [
    "What are the latest mortgage KPIs?",
    "How did mortgage lending perform over the last 12 months?",
    "What happened to delinquency and credit risk over the last 12 months?",
]


for question in questions:

    print("\n" + "=" * 80)
    print("USER:", question)
    print("=" * 80)

    answer = ask_claude(question)

    print("CLAUDE:")
    print(answer)