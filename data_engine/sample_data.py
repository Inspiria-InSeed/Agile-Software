
import pandas as pd
from datetime import date, timedelta

from data_engine.analytics import (
    calculate_sprint_metrics,
    calculate_developer_workload,
    calculate_priority_analysis,
    calculate_overdue_tasks,
    calculate_sprint_comparison
)


# -----------------------------------------
# 1. SAMPLE SPRINT TASK DATA
# -----------------------------------------

tasks = [

    {
        "task_id": 1,
        "task_name": "Login Page",
        "assigned_to": "Aarav",
        "sprint": "Sprint 1",
        "status": "Completed",
        "priority": "High",
        "story_points": 5,
        "due_date": date.today() - timedelta(days=3)
    },

    {
        "task_id": 2,
        "task_name": "Dashboard Design",
        "assigned_to": "Priya",
        "sprint": "Sprint 1",
        "status": "In Progress",
        "priority": "Medium",
        "story_points": 8,
        "due_date": date.today() - timedelta(days=2)
    },

    {
        "task_id": 3,
        "task_name": "Database Setup",
        "assigned_to": "Rahul",
        "sprint": "Sprint 1",
        "status": "Completed",
        "priority": "High",
        "story_points": 5,
        "due_date": date.today() - timedelta(days=4)
    },

    {
        "task_id": 4,
        "task_name": "API Integration",
        "assigned_to": "Aarav",
        "sprint": "Sprint 1",
        "status": "Pending",
        "priority": "High",
        "story_points": 3,
        "due_date": date.today() - timedelta(days=1)
    },

    {
        "task_id": 5,
        "task_name": "Testing",
        "assigned_to": "Priya",
        "sprint": "Sprint 2",
        "status": "Completed",
        "priority": "Medium",
        "story_points": 5,
        "due_date": date.today() + timedelta(days=2)
    },

    {
        "task_id": 6,
        "task_name": "Bug Fixing",
        "assigned_to": "Rahul",
        "sprint": "Sprint 2",
        "status": "In Progress",
        "priority": "Low",
        "story_points": 3,
        "due_date": date.today() + timedelta(days=3)
    }
]


# -----------------------------------------
# 2. CREATE PANDAS DATAFRAME
# -----------------------------------------

df = pd.DataFrame(tasks)

print("\nSPRINT TASK DATA")
print(df.to_string(index=False))

print("\nTotal tasks:", len(df))


# -----------------------------------------
# 3. BASIC SPRINT PERFORMANCE
# -----------------------------------------

print("\nSPRINT PERFORMANCE")

for sprint in df["sprint"].unique():

    sprint_data = df[df["sprint"] == sprint]

    total_tasks = len(sprint_data)

    completed_tasks = len(
        sprint_data[sprint_data["status"] == "Completed"]
    )

    completion_rate = (
        completed_tasks / total_tasks * 100
        if total_tasks > 0 else 0
    )

    print("\n", sprint)
    print("Total Tasks:", total_tasks)
    print("Completed Tasks:", completed_tasks)
    print("Completion Rate:", round(completion_rate, 2), "%")


# -----------------------------------------
# 4. SPRINT ANALYSIS
# -----------------------------------------

results = calculate_sprint_metrics(df)

print("\nSPRINT ANALYSIS RESULTS")

for result in results:
    print(result)


# -----------------------------------------
# 5. DEVELOPER WORKLOAD ANALYSIS
# -----------------------------------------

workload = calculate_developer_workload(df)

print("\nDEVELOPER WORKLOAD ANALYSIS")

for developer in workload:
    print(developer)


# -----------------------------------------
# 6. PRIORITY ANALYSIS
# -----------------------------------------

priority_results = calculate_priority_analysis(df)

print("\nPRIORITY ANALYSIS")

for result in priority_results:
    print(result)


# -----------------------------------------
# 7. OVERDUE TASK ANALYSIS
# -----------------------------------------

overdue = calculate_overdue_tasks(df)

print("\nOVERDUE TASK ANALYSIS")

print("Total Overdue Tasks:", len(overdue))

for task in overdue:
    print(task)

# SPRINT COMPARISON ANALYSIS

comparison = calculate_sprint_comparison(df)

print("\nSPRINT COMPARISON ANALYSIS")

for key, value in comparison.items():
    print(key, ":", value)