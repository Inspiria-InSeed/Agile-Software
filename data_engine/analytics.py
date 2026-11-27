import pandas as pd
def calculate_sprint_metrics(df):

    sprint_results = []

    # Get all unique sprint names
    sprints = df["sprint"].unique()

    for sprint in sprints:

        # Filter tasks for the current sprint
        sprint_data = df[df["sprint"] == sprint]

        # Count tasks
        total_tasks = len(sprint_data)

        completed_tasks = len(
            sprint_data[sprint_data["status"] == "Completed"]
        )

        in_progress_tasks = len(
            sprint_data[sprint_data["status"] == "In Progress"]
        )

        pending_tasks = len(
            sprint_data[sprint_data["status"] == "Pending"]
        )

        # Calculate task completion percentage
        completion_rate = (
            completed_tasks / total_tasks * 100
            if total_tasks > 0 else 0
        )

        # Calculate story points
        total_story_points = int(
            sprint_data["story_points"].sum()
        )

        completed_story_points = int(
            sprint_data[
                sprint_data["status"] == "Completed"
            ]["story_points"].sum()
        )

        # Calculate story point completion percentage
        story_point_completion_rate = (
            completed_story_points / total_story_points * 100
            if total_story_points > 0 else 0
        )

        # Store sprint results
        sprint_results.append({

            "sprint": sprint,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "in_progress_tasks": in_progress_tasks,
            "pending_tasks": pending_tasks,
            "completion_rate": round(completion_rate, 2),

            "total_story_points": total_story_points,
            "completed_story_points": completed_story_points,
            "story_point_completion_rate": round(
                story_point_completion_rate, 2
            )
        })

    return sprint_results


# ------------------------------------------------
# DEVELOPER WORKLOAD ANALYSIS
# ------------------------------------------------

def calculate_developer_workload(df):

    developer_results = []

    # Get unique developer names
    developers = df["assigned_to"].unique()

    for developer in developers:

        # Filter tasks assigned to this developer
        developer_data = df[
            df["assigned_to"] == developer
        ]

        # Count total tasks
        total_tasks = len(developer_data)

        # Count completed tasks
        completed_tasks = len(
            developer_data[
                developer_data["status"] == "Completed"
            ]
        )

        # Count pending tasks
        pending_tasks = len(
            developer_data[
                developer_data["status"] == "Pending"
            ]
        )

        # Count in-progress tasks
        in_progress_tasks = len(
            developer_data[
                developer_data["status"] == "In Progress"
            ]
        )

        # Store developer results
        developer_results.append({

            "developer": developer,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "in_progress_tasks": in_progress_tasks

        })

    return developer_results

def calculate_priority_analysis(df):

    priority_results = []

    # Get all unique priorities
    priorities = df["priority"].unique()

    for priority in priorities:

        # Filter tasks by priority
        priority_data = df[df["priority"] == priority]

        total_tasks = len(priority_data)

        completed_tasks = len(
            priority_data[priority_data["status"] == "Completed"]
        )

        pending_tasks = len(
            priority_data[priority_data["status"] == "Pending"]
        )

        in_progress_tasks = len(
            priority_data[priority_data["status"] == "In Progress"]
        )

        # Store results
        priority_results.append({
            "priority": priority,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "in_progress_tasks": in_progress_tasks
        })

    return priority_results

def calculate_overdue_tasks(df):

    from datetime import date

    # Get today's date
    today = date.today()

    # Convert due_date column into date format
    df["due_date"] = pd.to_datetime(
        df["due_date"]
    ).dt.date

    # Find tasks that are overdue and not completed
    overdue_data = df[
        (df["due_date"] < today) &
        (df["status"] != "Completed")
    ]

    # Convert results into a list of dictionaries
    overdue_tasks = overdue_data[
        ["task_name", "assigned_to", "sprint",
         "status", "due_date"]
    ].to_dict(orient="records")

    return overdue_tasks


def calculate_sprint_comparison(df):

    comparison_results = []

    # Get all sprint names
    sprints = df["sprint"].dropna().unique()

    # Calculate metrics for each sprint
    for sprint in sprints:

        sprint_data = df[df["sprint"] == sprint]

        total_tasks = len(sprint_data)

        completed_tasks = len(
            sprint_data[sprint_data["status"] == "Completed"]
        )

        pending_tasks = len(
            sprint_data[sprint_data["status"] == "Pending"]
        )

        total_story_points = int(
            sprint_data["story_points"].sum()
        )

        completed_story_points = int(
            sprint_data[
                sprint_data["status"] == "Completed"
            ]["story_points"].sum()
        )

        completion_rate = (
            completed_tasks / total_tasks * 100
            if total_tasks > 0 else 0
        )

        comparison_results.append({
            "sprint": sprint,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "completion_rate": round(completion_rate, 2),
            "total_story_points": total_story_points,
            "completed_story_points": completed_story_points
        })

    # Check whether at least two sprints exist
    if len(comparison_results) < 2:
        return {"message": "At least two sprints are required."}

    # Find sprint with highest completion rate
    best_completion = max(
        comparison_results,
        key=lambda x: x["completion_rate"]
    )

    # Find sprint with most completed story points
    best_story_points = max(
        comparison_results,
        key=lambda x: x["completed_story_points"]
    )

    # Find sprint with most pending tasks
    most_pending = max(
        comparison_results,
        key=lambda x: x["pending_tasks"]
    )

    return {
        "sprint_metrics": comparison_results,
        "highest_completion_rate": best_completion["sprint"],
        "most_completed_story_points": best_story_points["sprint"],
        "most_pending_tasks": most_pending["sprint"]
    }
