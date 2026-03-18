import json
from datetime import datetime, timedelta, timezone

import requests


def _calculate_streaks(submission_calendar: dict) -> tuple[int, int]:
    active_days = sorted(
        datetime.fromtimestamp(int(timestamp), tz=timezone.utc).date()
        for timestamp, count in submission_calendar.items()
        if int(count) > 0
    )

    if not active_days:
        return 0, 0

    longest_streak = 1
    running_streak = 1

    for previous, current in zip(active_days, active_days[1:]):
        if current == previous + timedelta(days=1):
            running_streak += 1
            longest_streak = max(longest_streak, running_streak)
        elif current != previous:
            running_streak = 1

    latest_day = active_days[-1]
    today = datetime.now(timezone.utc).date()
    if latest_day < today - timedelta(days=1):
        current_streak = 0
    else:
        current_streak = 1
        index = len(active_days) - 1
        while index > 0 and active_days[index] == active_days[index - 1] + timedelta(days=1):
            current_streak += 1
            index -= 1

    return current_streak, longest_streak


def get_leetcode_stats(username: str):
    url = "https://leetcode.com/graphql/"
    query = """
    query getUserProfile($username: String!) {
      allQuestionsCount {
        difficulty
        count
      }
      matchedUser(username: $username) {
        username
        profile {
          ranking
        }
        userCalendar {
          submissionCalendar
        }
        submitStats: submitStatsGlobal {
          acSubmissionNum {
            difficulty
            count
          }
        }
      }
    }
    """

    payload = {
        "query": query,
        "variables": {"username": username},
        "operationName": "getUserProfile",
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException:
        raise ValueError("Failed to fetch data from LeetCode")

    user = data["data"].get("matchedUser")
    if user is None:
        raise ValueError("LeetCode user not found")

    stats_list = user["submitStats"]["acSubmissionNum"]
    totals_list = data["data"].get("allQuestionsCount", [])

    stats_by_difficulty = {}
    for item in stats_list:
        stats_by_difficulty[item["difficulty"]] = item["count"]

    totals_by_difficulty = {}
    for item in totals_list:
        totals_by_difficulty[item["difficulty"]] = item["count"]

    calendar_raw = user.get("userCalendar", {}).get("submissionCalendar", "{}")
    try:
        submission_calendar = json.loads(calendar_raw)
    except json.JSONDecodeError:
        submission_calendar = {}
    current_streak, longest_streak = _calculate_streaks(submission_calendar)

    return {
        "username": user["username"],
        "ranking": user.get("profile", {}).get("ranking", 0),
        "total_solved": stats_by_difficulty.get("All", 0),
        "easy_solved": stats_by_difficulty.get("Easy", 0),
        "medium_solved": stats_by_difficulty.get("Medium", 0),
        "hard_solved": stats_by_difficulty.get("Hard", 0),
        "total_available": totals_by_difficulty.get("All", 0),
        "easy_total": totals_by_difficulty.get("Easy", 0),
        "medium_total": totals_by_difficulty.get("Medium", 0),
        "hard_total": totals_by_difficulty.get("Hard", 0),
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "submission_calendar": submission_calendar,
    }
