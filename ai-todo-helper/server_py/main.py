import os
import sqlite3
import re
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict
from datetime import datetime, date

from dotenv import load_dotenv
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not set in environment.")
import google.generativeai as genai
genai.configure(api_key=GEMINI_API_KEY)

DATABASE_PATH = "todo.db"

def init_db():
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS goal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            start_date DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS task (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            goal_id INTEGER NOT NULL,
            phase TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            due_date DATE,
            completed BOOLEAN DEFAULT 0,
            "order" INTEGER,
            FOREIGN KEY (goal_id) REFERENCES goal (id) ON DELETE CASCADE
        )
        """)
        conn.commit()

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
@app.on_event("startup")
def on_startup():
    init_db()

class GoalCreate(BaseModel):
    title: str
    start_date: date

class TaskRead(BaseModel):
    id: int
    title: str
    description: str
    due_date: date
    completed: bool
    order: int

class GoalRead(BaseModel):
    id: int
    title: str
    start_date: date
    created_at: datetime
    completion: float
    phases: Dict[str, List[TaskRead]]

def generate_intelligent_plan(goal_title: str, start_date: date):
    duration_match = re.search(r"in (\d+)\s+(week|month)s?", goal_title, re.IGNORECASE)
    if not duration_match:
        total_duration_weeks = 4
    else:
        num, unit = duration_match.groups()
        total_duration_weeks = int(num) * 4 if 'month' in unit else int(num)

    prompt = f"""
    Act as an expert project manager. A user has the following goal: "{goal_title}".
    Their desired start date is {start_date.isoformat()}.
    The goal should be completed in approximately {total_duration_weeks} weeks.

    Your task is to create a detailed, actionable plan. Break the plan down into logical phases (e.g., "Week 1: Foundations", "Week 2: Core Concepts").
    For each phase, create a list of specific tasks. Each task must have:
    1. A short, clear `title`.
    2. A one-sentence `description` explaining its purpose.
    3. A calculated `due_date` based on the start date and logical progression. Distribute tasks evenly.

    Return the entire plan as a single, valid JSON object. Do not include any text or markdown before or after the JSON.
    The JSON structure must be:
    {{
      "phases": [
        {{
          "phase_title": "string",
          "tasks": [
            {{
              "task_title": "string",
              "description": "string",
              "due_date": "YYYY-MM-DD"
            }}
          ]
        }}
      ]
    }}
    """
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(cleaned_response)
    except (json.JSONDecodeError, Exception) as e:
        print(f"Error parsing AI response: {e}")
        raise HTTPException(status_code=500, detail="Failed to get a valid plan from the AI service.")


def is_plan_relevant(goal_title: str, plan: dict) -> bool:
    plan_summary = " ".join([task.get('task_title', '') for phase in plan.get('phases', []) for task in phase.get('tasks', [])])
    if not plan_summary.strip():
        return False

    prompt = f"""
    Original Goal: "{goal_title}"
    Generated Plan Summary: "{plan_summary}"

    Is the generated plan a direct and logical breakdown of the original goal?
    Answer ONLY with the word "Yes" or "No".
    """
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        if "no" in response.text.lower():
            print(f"AI Validation Failed: Goal '{goal_title}' was deemed irrelevant to the plan.")
            return False
        return True
    except Exception as e:
        print(f"An error occurred during AI validation: {e}")
        return True

@app.post("/api/goals", response_model=GoalRead)
def create_goal(goal: GoalCreate):
    plan = generate_intelligent_plan(goal.title, goal.start_date)
    if not is_plan_relevant(goal.title, plan):
        raise HTTPException(
            status_code=400,
            detail="The AI could not create a meaningful plan for this goal. Please try a more specific or different goal."
        )
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO goal (title, start_date) VALUES (?, ?)", (goal.title, goal.start_date))
            goal_id = cursor.lastrowid
            
            task_order = 0
            for phase in plan.get("phases", []):
                phase_title = phase.get("phase_title", "Unnamed Phase")
                for task in phase.get("tasks", []):
                    cursor.execute(
                        """
                        INSERT INTO task (goal_id, phase, title, description, due_date, "order")
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            goal_id,
                            phase_title,
                            task.get("task_title"),
                            task.get("description"),
                            task.get("due_date"),
                            task_order
                        )
                    )
                    task_order += 1
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {e}")

    return get_goal(goal_id)

def fetch_goal_data(goal_id: int, conn: sqlite3.Connection) -> dict:
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM goal WHERE id = ?", (goal_id,))
    goal = cursor.fetchone()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    cursor.execute("SELECT * FROM task WHERE goal_id = ? ORDER BY due_date, \"order\"", (goal_id,))
    tasks_raw = cursor.fetchall()

    phases_dict = {}
    for task in tasks_raw:
        phase_title = task["phase"]
        if phase_title not in phases_dict:
            phases_dict[phase_title] = []
        phases_dict[phase_title].append(dict(task))

    completed_tasks = sum(1 for task in tasks_raw if task["completed"])
    completion = (completed_tasks / len(tasks_raw)) if tasks_raw else 0.0

    return {
        "id": goal["id"],
        "title": goal["title"],
        "start_date": goal["start_date"],
        "created_at": goal["created_at"],
        "completion": completion,
        "phases": phases_dict
    }

@app.get("/api/goals/{goal_id}", response_model=GoalRead)
def get_goal(goal_id: int):
    with sqlite3.connect(DATABASE_PATH) as conn:
        goal_data = fetch_goal_data(goal_id, conn)
        return GoalRead.model_validate(goal_data)

@app.get("/api/goals", response_model=List[GoalRead])
def list_goals():
    goals_data = []
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM goal ORDER BY created_at DESC")
        goal_ids = cursor.fetchall()
        
        for goal_id_row in goal_ids:
            goal_data_dict = fetch_goal_data(goal_id_row['id'], conn)
            goals_data.append(GoalRead.model_validate(goal_data_dict))
            
    return goals_data

@app.patch("/api/tasks/{task_id}/toggle", status_code=204)
def toggle_task(task_id: int):
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE task SET completed = NOT completed WHERE id = ?", (task_id,))
        conn.commit()

@app.delete("/api/goals/{goal_id}", status_code=204)
def delete_goal(goal_id: int):
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM goal WHERE id = ?", (goal_id,))
        conn.commit()