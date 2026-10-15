"""
Quiz Application - GUI Version (Tkinter)
========================================
Optional GUI using Tkinter as mentioned in the assignment.

Features:
- Category selection
- Timer-based questions
- Negative marking
- Score display
- Leaderboard

Run: python quiz_gui.py
"""

import json
import random
import time
import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime


# ============================================================
# CONFIGURATION
# ============================================================
QUESTIONS_FILE = "questions.json"
LEADERBOARD_FILE = "leaderboard.json"
TIME_PER_QUESTION = 30
CORRECT_MARKS = 4
NEGATIVE_MARKS = -1
NUM_QUESTIONS = 5


class QuizGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Quiz Application - MCA Project")
        self.root.geometry("700x550")
        self.root.resizable(False, False)
        self.root.configure(bg="#1e1e2e")

        self.questions_data = self.load_questions()
        self.score = 0
        self.correct_count = 0
        self.current_q = 0
        self.selected_questions = []
        self.category = ""
        self.player_name = ""
        self.timer_seconds = TIME_PER_QUESTION
        self.timer_id = None
        self.answered = False

        self.setup_styles()
        self.show_home_screen()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 11), padding=8)
        style.configure("Title.TLabel", font=("Segoe UI", 20, "bold"),
                        background="#1e1e2e", foreground="#cdd6f4")
        style.configure("Normal.TLabel", font=("Segoe UI", 12),
                        background="#1e1e2e", foreground="#cdd6f4")
        style.configure("Score.TLabel", font=("Segoe UI", 14, "bold"),
                        background="#1e1e2e", foreground="#a6e3a1")

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def load_questions(self):
        try:
            with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"Could not load questions: {e}")
            return {}

    def load_leaderboard(self):
        if not os.path.exists(LEADERBOARD_FILE):
            return []
        try:
            with open(LEADERBOARD_FILE, "r") as f:
                return json.load(f)
        except:
            return []

    def save_leaderboard(self, leaderboard):
        try:
            with open(LEADERBOARD_FILE, "w") as f:
                json.dump(leaderboard, f, indent=4)
        except:
            pass

    def update_leaderboard(self):
        leaderboard = self.load_leaderboard()
        entry = {
            "name": self.player_name,
            "score": self.score,
            "category": self.category,
            "total_questions": NUM_QUESTIONS,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        leaderboard.append(entry)
        leaderboard.sort(key=lambda x: x["score"], reverse=True)
        leaderboard = leaderboard[:10]
        self.save_leaderboard(leaderboard)

    # ============================================================
    # SCREENS
    # ============================================================

    def show_home_screen(self):
        self.clear_window()

        frame = tk.Frame(self.root, bg="#1e1e2e")
        frame.pack(expand=True)

        ttk.Label(frame, text="🎯 QUIZ APPLICATION", style="Title.TLabel").pack(pady=20)
        ttk.Label(frame, text="MCA III Semester Project", style="Normal.TLabel").pack(pady=5)

        btn_frame = tk.Frame(frame, bg="#1e1e2e")
        btn_frame.pack(pady=40)

        tk.Button(btn_frame, text="Start New Quiz", width=20, height=2,
                  font=("Segoe UI", 12, "bold"), bg="#89b4fa", fg="#1e1e2e",
                  activebackground="#74c7ec", command=self.start_quiz_flow).pack(pady=10)

        tk.Button(btn_frame, text="View Leaderboard", width=20, height=2,
                  font=("Segoe UI", 12), bg="#a6e3a1", fg="#1e1e2e",
                  activebackground="#94e2d5", command=self.show_leaderboard).pack(pady=10)

        tk.Button(btn_frame, text="Exit", width=20, height=2,
                  font=("Segoe UI", 12), bg="#f38ba8", fg="#1e1e2e",
                  activebackground="#eba0ac", command=self.root.quit).pack(pady=10)

    def start_quiz_flow(self):
        if not self.questions_data:
            messagebox.showerror("Error", "No questions available!")
            return

        name = simpledialog.askstring("Player Name", "Enter your name:", parent=self.root)
        if not name or not name.strip():
            messagebox.showwarning("Warning", "Name is required!")
            return
        self.player_name = name.strip()

        # Category selection window
        self.clear_window()
        frame = tk.Frame(self.root, bg="#1e1e2e")
        frame.pack(expand=True)

        ttk.Label(frame, text="Select Category", style="Title.TLabel").pack(pady=20)

        categories = list(self.questions_data.keys())
        self.cat_var = tk.StringVar(value=categories[0])

        for cat in categories:
            count = len(self.questions_data[cat])
            rb = tk.Radiobutton(frame, text=f"{cat} ({count} Qs)", variable=self.cat_var,
                                value=cat, font=("Segoe UI", 12), bg="#1e1e2e",
                                fg="#cdd6f4", selectcolor="#313244",
                                activebackground="#1e1e2e", activeforeground="#89b4fa")
            rb.pack(anchor="w", padx=100, pady=5)

        tk.Button(frame, text="Start Quiz →", width=15, font=("Segoe UI", 12, "bold"),
                  bg="#89b4fa", fg="#1e1e2e", command=self.begin_quiz).pack(pady=30)

        tk.Button(frame, text="← Back", width=10, font=("Segoe UI", 10),
                  bg="#6c7086", fg="white", command=self.show_home_screen).pack()

    def begin_quiz(self):
        self.category = self.cat_var.get()
        available = self.questions_data[self.category]
        n = min(NUM_QUESTIONS, len(available))
        self.selected_questions = random.sample(available, n)
        self.score = 0
        self.correct_count = 0
        self.current_q = 0
        self.show_question()

    def show_question(self):
        self.clear_window()
        self.answered = False
        self.timer_seconds = TIME_PER_QUESTION

        q = self.selected_questions[self.current_q]
        total = len(self.selected_questions)

        # Header
        header = tk.Frame(self.root, bg="#313244", height=50)
        header.pack(fill="x")
        tk.Label(header, text=f"Q {self.current_q + 1}/{total}  |  {self.category}",
                 font=("Segoe UI", 12, "bold"), bg="#313244", fg="#cdd6f4").pack(side="left", padx=15, pady=10)
        self.timer_label = tk.Label(header, text=f"⏱ {self.timer_seconds}s",
                                    font=("Segoe UI", 12, "bold"), bg="#313244", fg="#f9e2af")
        self.timer_label.pack(side="right", padx=15)
        self.score_label = tk.Label(header, text=f"Score: {self.score}",
                                    font=("Segoe UI", 12), bg="#313244", fg="#a6e3a1")
        self.score_label.pack(side="right", padx=15)

        # Question
        q_frame = tk.Frame(self.root, bg="#1e1e2e")
        q_frame.pack(fill="both", expand=True, padx=30, pady=20)

        tk.Label(q_frame, text=q["question"], font=("Segoe UI", 14),
                 bg="#1e1e2e", fg="#cdd6f4", wraplength=600, justify="left").pack(anchor="w", pady=15)

        self.option_var = tk.IntVar(value=-1)
        self.option_buttons = []

        for i, opt in enumerate(q["options"]):
            rb = tk.Radiobutton(q_frame, text=opt, variable=self.option_var, value=i,
                                font=("Segoe UI", 12), bg="#1e1e2e", fg="#cdd6f4",
                                selectcolor="#45475a", activebackground="#1e1e2e",
                                activeforeground="#89b4fa", wraplength=550, justify="left")
            rb.pack(anchor="w", pady=6)
            self.option_buttons.append(rb)

        # Submit button
        btn_frame = tk.Frame(self.root, bg="#1e1e2e")
        btn_frame.pack(pady=15)
        self.submit_btn = tk.Button(btn_frame, text="Submit Answer", font=("Segoe UI", 12, "bold"),
                                    bg="#89b4fa", fg="#1e1e2e", width=15,
                                    command=self.submit_answer)
        self.submit_btn.pack()

        # Start timer
        self.update_timer()

    def update_timer(self):
        if self.answered:
            return
        self.timer_label.config(text=f"⏱ {self.timer_seconds}s")
        if self.timer_seconds <= 0:
            self.time_up()
            return
        self.timer_seconds -= 1
        self.timer_id = self.root.after(1000, self.update_timer)

    def time_up(self):
        if self.answered:
            return
        self.answered = True
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        messagebox.showinfo("Time's Up!", "You ran out of time!")
        self.next_question()

    def submit_answer(self):
        if self.answered:
            return
        selected = self.option_var.get()
        if selected == -1:
            messagebox.showwarning("Warning", "Please select an option!")
            return

        self.answered = True
        if self.timer_id:
            self.root.after_cancel(self.timer_id)

        q = self.selected_questions[self.current_q]
        correct_idx = q["answer"]

        if selected == correct_idx:
            self.score += CORRECT_MARKS
            self.correct_count += 1
            msg = f"✅ Correct! +{CORRECT_MARKS} marks"
            if "explanation" in q:
                msg += f"\n\n💡 {q['explanation']}"
            messagebox.showinfo("Result", msg)
        else:
            self.score += NEGATIVE_MARKS
            correct_ans = q["options"][correct_idx]
            msg = f"❌ Wrong! Correct: {correct_ans}\n({NEGATIVE_MARKS} marks)"
            if "explanation" in q:
                msg += f"\n\n💡 {q['explanation']}"
            messagebox.showinfo("Result", msg)

        self.score_label.config(text=f"Score: {self.score}")
        self.next_question()

    def next_question(self):
        self.current_q += 1
        if self.current_q < len(self.selected_questions):
            self.show_question()
        else:
            self.show_result()

    def show_result(self):
        self.clear_window()
        self.update_leaderboard()

        frame = tk.Frame(self.root, bg="#1e1e2e")
        frame.pack(expand=True)

        ttk.Label(frame, text="🏆 QUIZ COMPLETED!", style="Title.TLabel").pack(pady=20)

        result_text = (
            f"Player   : {self.player_name}\n"
            f"Category : {self.category}\n"
            f"Correct  : {self.correct_count}/{len(self.selected_questions)}\n"
            f"Score    : {self.score}"
        )
        tk.Label(frame, text=result_text, font=("Segoe UI", 14),
                 bg="#1e1e2e", fg="#cdd6f4", justify="left").pack(pady=15)

        tk.Button(frame, text="View Leaderboard", width=18, font=("Segoe UI", 11),
                  bg="#a6e3a1", fg="#1e1e2e", command=self.show_leaderboard).pack(pady=8)
        tk.Button(frame, text="Play Again", width=18, font=("Segoe UI", 11),
                  bg="#89b4fa", fg="#1e1e2e", command=self.start_quiz_flow).pack(pady=8)
        tk.Button(frame, text="Home", width=18, font=("Segoe UI", 11),
                  bg="#6c7086", fg="white", command=self.show_home_screen).pack(pady=8)

    def show_leaderboard(self):
        self.clear_window()
        frame = tk.Frame(self.root, bg="#1e1e2e")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ttk.Label(frame, text="🏆 LEADERBOARD (Top 10)", style="Title.TLabel").pack(pady=10)

        leaderboard = self.load_leaderboard()

        if not leaderboard:
            tk.Label(frame, text="No records yet. Be the first!",
                     font=("Segoe UI", 12), bg="#1e1e2e", fg="#cdd6f4").pack(pady=30)
        else:
            # Table header
            header = tk.Frame(frame, bg="#313244")
            header.pack(fill="x", pady=5)
            for text, width in [("Rank", 6), ("Name", 15), ("Score", 8), ("Category", 18), ("Date", 18)]:
                tk.Label(header, text=text, font=("Segoe UI", 10, "bold"),
                         bg="#313244", fg="#cdd6f4", width=width).pack(side="left", padx=2)

            for i, entry in enumerate(leaderboard, 1):
                row = tk.Frame(frame, bg="#1e1e2e")
                row.pack(fill="x", pady=2)
                values = [str(i), entry["name"], str(entry["score"]),
                          entry["category"], entry["date"][:16]]
                widths = [6, 15, 8, 18, 18]
                for val, w in zip(values, widths):
                    tk.Label(row, text=val, font=("Segoe UI", 10),
                             bg="#1e1e2e", fg="#cdd6f4", width=w).pack(side="left", padx=2)

        tk.Button(frame, text="← Back to Home", font=("Segoe UI", 11),
                  bg="#6c7086", fg="white", command=self.show_home_screen).pack(pady=20)


# ============================================================
# ENTRY POINT
# ============================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = QuizGUI(root)
    root.mainloop()
