"""Entry point for demonstrating both Agentic AI Coworker prototypes."""

from agent1_daily_tech_upgrade import generate_daily_brief
from agent2_career_coach import interactive_session


def main() -> None:
    while True:
        print("\nPersonal Agentic AI Coworkers")
        print("1. Generate DailyTechUpgradeAgent brief")
        print("2. Start career coaching session")
        print("3. Exit")
        choice = input("Choose an option: ").strip()
        if choice == "1":
            print("\n" + generate_daily_brief())
        elif choice == "2":
            interactive_session()
        elif choice == "3":
            print("Goodbye!")
            return
        else:
            print("Please choose 1, 2, or 3.")


if __name__ == "__main__":
    main()
