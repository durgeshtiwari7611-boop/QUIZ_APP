"""
Quiz Application
================
Features:
- Random question selection from JSON file
- Category-based quiz support
- Timer-based quiz system
- Negative marking scheme
- Leaderboard generation
- Modular & well-commented code
- Exception handling

Author: MCA III Semester Student
"""

import json
import random
import time
import os
from datetime import datetime


# ============================================================
# CONFIGURATION
# ============================================================
QUESTIONS_FILE = "questions.json"
LEADERBOARD_FILE = "leaderboard.json"
TIME_PER_QUESTION = 30          # seconds per question
CORRECT_MARKS = 4               # marks for correct answer
NEGATIVE_MARKS = -1             # marks for wrong answer
NUM_QUESTIONS = 5               # number of questions per quiz


# ============================================================
# DATA HANDLING FUNCTIONS
# ============================================================

def load_questions():
    """Load questions from JSON file with error handling."""
    try:
        with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not data:
            raise ValueError("Questions file is empty!")
        return data
    except FileNotFoundError:
        print(f"[ERROR] '{QUESTIONS_FILE}' not found!")
        return {}
    except json.JSONDecodeError:
        print("[ERROR] Invalid JSON format in questions file!")
        return {}
    except Exception as e:
        print(f"[ERROR] Failed to load questions: {e}")
        return {}


def load_leaderboard():
    """Load leaderboard from JSON file."""
    if not os.path.exists(LEADERBOARD_FILE):
        return []
    try:
        with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, Exception):
        return []


def save_leaderboard(leaderboard):
    """Save leaderboard to JSON file."""
    try:
        with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
            json.dump(leaderboard, f, indent=4)
    except Exception as e:
        print(f"[ERROR] Could not save leaderboard: {e}")


def update_leaderboard(name, score, category, total_questions):
    """Add a new entry to the leaderboard and keep top 10."""
    leaderboard = load_leaderboard()
    entry = {
        "name": name,
        "score": score,
        "category": category,
        "total_questions": total_questions,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    leaderboard.append(entry)
    # Sort by score descending
    leaderboard.sort(key=lambda x: x["score"], reverse=True)
    # Keep only top 10
    leaderboard = leaderboard[:10]
    save_leaderboard(leaderboard)
    return leaderboard


# ============================================================
# QUIZ LOGIC
# ============================================================

def display_categories(questions_data):
    """Display available categories and return list of category names."""
    categories = list(questions_data.keys())
    print("\n" + "=" * 50)
    print("           AVAILABLE CATEGORIES")
    print("=" * 50)
    for i, cat in enumerate(categories, 1):
        print(f"  {i}. {cat}  ({len(questions_data[cat])} questions)")
    print("=" * 50)
    return categories


def get_user_choice(prompt, min_val, max_val):
    """Get a valid integer choice from user with exception handling."""
    while True:
        try:
            choice = int(input(prompt))
            if min_val <= choice <= max_val:
                return choice
            else:
                print(f"Please enter a number between {min_val} and {max_val}.")
        except ValueError:
            print("Invalid input! Please enter a number.")
        except KeyboardInterrupt:
            print("\n\nQuiz interrupted by user.")
            exit(0)


def ask_question(question_data, q_num, total):
    """
    Ask a single question with timer.
    Returns: (is_correct, marks_obtained, time_taken)
    """
    print(f"\n{'─' * 50}")
    print(f"Question {q_num}/{total}")
    print(f"{'─' * 50}")
    print(f"Q: {question_data['question']}")
    print()

    options = question_data["options"]
    for i, opt in enumerate(options):
        print(f"   {i + 1}. {opt}")

    print(f"\n⏱  You have {TIME_PER_QUESTION} seconds to answer!")
    print("Enter your choice (1-4) or 0 to skip:")

    start_time = time.time()

    # Simple timer implementation using input with timeout simulation
    # (Note: true non-blocking timeout needs threading/select which is advanced)
    try:
        user_input = input("Your answer: ").strip()
        elapsed = time.time() - start_time

        if elapsed > TIME_PER_QUESTION:
            print(f"\n⏰ Time's up! You took {elapsed:.1f} seconds.")
            return False, 0, elapsed

        if user_input == "0" or user_input.lower() == "skip":
            print("Question skipped.")
            return False, 0, elapsed

        choice = int(user_input)
        if choice < 1 or choice > len(options):
            print("Invalid choice! Marked as wrong.")
            return False, NEGATIVE_MARKS, elapsed

        selected_index = choice - 1
        correct_index = question_data["answer"]

        if selected_index == correct_index:
            print(f"✅ Correct! (+{CORRECT_MARKS} marks)")
            if "explanation" in question_data:
                print(f"💡 {question_data['explanation']}")
            return True, CORRECT_MARKS, elapsed
        else:
            print(f"❌ Wrong! Correct answer was: {options[correct_index]}")
            print(f"   ({NEGATIVE_MARKS} marks)")
            if "explanation" in question_data:
                print(f"💡 {question_data['explanation']}")
            return False, NEGATIVE_MARKS, elapsed

    except ValueError:
        print("Invalid input! Marked as wrong.")
        return False, NEGATIVE_MARKS, time.time() - start_time
    except KeyboardInterrupt:
        print("\nQuiz interrupted.")
        return False, 0, time.time() - start_time


def run_quiz(questions_data, category, num_questions=NUM_QUESTIONS):
    """Run the quiz for selected category."""
    available = questions_data[category]

    if len(available) < num_questions:
        num_questions = len(available)
        print(f"\nOnly {num_questions} questions available in this category.")

    # Randomly select questions
    selected = random.sample(available, num_questions)

    print(f"\n{'=' * 50}")
    print(f"  Starting Quiz: {category}")
    print(f"  Questions: {num_questions}")
    print(f"  Marks: +{CORRECT_MARKS} correct | {NEGATIVE_MARKS} wrong")
    print(f"  Time per question: {TIME_PER_QUESTION} seconds")
    print(f"{'=' * 50}")

    score = 0
    correct_count = 0
    results = []

    for i, q in enumerate(selected, 1):
        is_correct, marks, time_taken = ask_question(q, i, num_questions)
        score += marks
        if is_correct:
            correct_count += 1
        results.append({
            "question": q["question"],
            "correct": is_correct,
            "marks": marks,
            "time": round(time_taken, 1)
        })

        # Small pause between questions
        time.sleep(0.5)

    return score, correct_count, num_questions, results


def show_result(name, score, correct, total, category, results):
    """Display final result summary."""
    print("\n" + "=" * 50)
    print("              QUIZ RESULT")
    print("=" * 50)
    print(f"  Player Name     : {name}")
    print(f"  Category        : {category}")
    print(f"  Correct Answers : {correct}/{total}")
    print(f"  Final Score     : {score}")
    print("=" * 50)

    print("\nDetailed Breakdown:")
    for i, r in enumerate(results, 1):
        status = "✅" if r["correct"] else "❌"
        print(f"  Q{i}: {status}  Marks: {r['marks']:+d}  Time: {r['time']}s")
        print(f"      {r['question'][:60]}...")

    # Update leaderboard
    leaderboard = update_leaderboard(name, score, category, total)
    print("\n🏆 Leaderboard Updated!")
    return leaderboard


def show_leaderboard():
    """Display the current leaderboard."""
    leaderboard = load_leaderboard()
    print("\n" + "=" * 60)
    print("                    🏆 LEADERBOARD (Top 10)")
    print("=" * 60)

    if not leaderboard:
        print("  No records yet. Be the first to play!")
        print("=" * 60)
        return

    print(f"{'Rank':<6}{'Name':<15}{'Score':<8}{'Category':<20}{'Date'}")
    print("-" * 60)
    for i, entry in enumerate(leaderboard, 1):
        print(f"{i:<6}{entry['name']:<15}{entry['score']:<8}"
              f"{entry['category']:<20}{entry['date']}")
    print("=" * 60)


# ============================================================
# MAIN MENU
# ============================================================

def main():
    """Main function to run the Quiz Application."""
    print("\n" + "█" * 50)
    print("█" + " " * 48 + "█")
    print("█" + "     WELCOME TO QUIZ APPLICATION".center(48) + "█")
    print("█" + " " * 48 + "█")
    print("█" * 50)

    questions_data = load_questions()
    if not questions_data:
        print("Cannot start quiz without questions. Exiting...")
        return

    while True:
        print("\n" + "─" * 40)
        print("           MAIN MENU")
        print("─" * 40)
        print("  1. Start New Quiz")
        print("  2. View Leaderboard")
        print("  3. Exit")
        print("─" * 40)

        choice = get_user_choice("Enter your choice (1-3): ", 1, 3)

        if choice == 1:
            # Get player name
            while True:
                name = input("\nEnter your name: ").strip()
                if name:
                    break
                print("Name cannot be empty!")

            # Select category
            categories = display_categories(questions_data)
            cat_choice = get_user_choice(
                f"\nSelect category (1-{len(categories)}): ",
                1, len(categories)
            )
            selected_category = categories[cat_choice - 1]

            # Run the quiz
            score, correct, total, results = run_quiz(
                questions_data, selected_category
            )

            # Show result
            show_result(name, score, correct, total, selected_category, results)

        elif choice == 2:
            show_leaderboard()

        elif choice == 3:
            print("\nThank you for playing! Goodbye 👋")
            break


# ============================================================
# ENTRY POINT
# ============================================================
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram terminated by user. Goodbye!")
    except Exception as e:
        print(f"\n[UNEXPECTED ERROR] {e}")
