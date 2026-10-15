# Quiz Application

**MCA III Semester – Python Programming Project**

## Features Implemented

- ✅ Random question selection from JSON file
- ✅ Category-based quiz support (General Knowledge, Science, Python Programming, Mathematics)
- ✅ Timer-based quiz system (30 seconds per question)
- ✅ Negative marking scheme (+4 correct, -1 wrong)
- ✅ Leaderboard generation (Top 10 players)
- ✅ Optional GUI using Tkinter
- ✅ Exception handling for invalid inputs
- ✅ Modular and well-commented code

## How to Run

### 1. Console Version (Recommended for Viva)
```bash
python quiz_app.py
```

### 2. GUI Version (Tkinter)
```bash
python quiz_gui.py
```

## Project Structure
```
Quiz_Application/
├── questions.json      # Question bank (4 categories)
├── quiz_app.py         # Console-based Quiz Application
├── quiz_gui.py         # GUI version using Tkinter
├── leaderboard.json    # Auto-generated after playing
└── README.md           # This file
```

## Marking Scheme
| Result       | Marks |
|--------------|-------|
| Correct      | +4    |
| Wrong        | -1    |
| Skip / Timeout | 0   |

## How to Add More Questions
Edit `questions.json` and add questions in the existing format:

```json
{
  "Category Name": [
    {
      "question": "Your question?",
      "options": ["A", "B", "C", "D"],
      "answer": 0,
      "explanation": "Optional explanation"
    }
  ]
}
```
`answer` is the **0-based index** of the correct option.

## Requirements
- Python 3.6+
- No external libraries required (uses only standard library)
- Tkinter (usually pre-installed with Python)

## Author
MCA III Semester Student
