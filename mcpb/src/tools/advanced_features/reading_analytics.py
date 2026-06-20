"""Reading analytics and statistics for CalibreMCP."""

import statistics
from collections import defaultdict
from datetime import date, datetime, timedelta

from pydantic import BaseModel, Field

try:
    from fastmcp import MCPTool
except ImportError:
    from ..compat import MCPTool


# Models
class ReadingSession(BaseModel):
    """Represents a single reading session."""

    book_id: str
    start_time: datetime
    end_time: datetime
    pages_read: int | None = None
    location: str | None = None  # For e-books with location-based progress
    progress_start: float | None = None  # 0.0 to 1.0
    progress_end: float | None = None  # 0.0 to 1.0

    @property
    def duration_minutes(self) -> float:
        """Calculate session duration in minutes."""
        return (self.end_time - self.start_time).total_seconds() / 60

    @property
    def pages_per_minute(self) -> float | None:
        """Calculate reading speed in pages per minute."""
        if self.pages_read and self.duration_minutes > 0:
            return self.pages_read / self.duration_minutes
        return None


class ReadingGoal(BaseModel):
    """Reading goal configuration."""

    id: str
    name: str
    target: int  # Target number (e.g., number of books, pages, or minutes)
    metric: str  # 'books', 'pages', 'minutes', 'days'
    period: str  # 'day', 'week', 'month', 'year', 'custom'
    start_date: date
    end_date: date | None = None  # For custom periods
    current_progress: int = 0
    is_completed: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def update_progress(self, progress: int) -> None:
        """Update goal progress."""
        self.current_progress = progress
        self.is_completed = self.current_progress >= self.target
        self.updated_at = datetime.utcnow()

    @property
    def progress_percentage(self) -> float:
        """Get progress as a percentage."""
        return min(100.0, (self.current_progress / self.target) * 100) if self.target > 0 else 0.0

    @property
    def remaining(self) -> int:
        """Get remaining amount to reach the goal."""
        return max(0, self.target - self.current_progress)

    @property
    def days_remaining(self) -> int | None:
        """Get days remaining until the goal deadline."""
        if not self.end_date:
            return None
        return max(0, (self.end_date - date.today()).days)

    @property
    def daily_target(self) -> float | None:
        """Get daily target to reach the goal."""
        if not self.end_date:
            return None
        days_remaining = (self.end_date - date.today()).days + 1
        if days_remaining <= 0:
            return None
        return self.remaining / days_remaining


# Main tool
class ReadingAnalyticsTool(MCPTool):
    """Track and analyze reading habits and statistics."""

    name = "reading_analytics"
    description = "Track and analyze reading statistics and habits"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._sessions = []  # In-memory storage (replace with database in production)
        self._goals = {}  # In-memory storage for reading goals

    async def _run(self, action: str, **kwargs) -> dict:
        """Route to the appropriate analytics handler."""
        handler = getattr(self, f"analytics_{action}", None)
        if not handler:
            return {"error": f"Unknown analytics action: {action}", "success": False}

        try:
            return await handler(**kwargs)
        except Exception as e:
            return {"error": str(e), "success": False}

    # Session Tracking
    async def analytics_start_session(self, book_id: str, **kwargs) -> dict:
        """Start a new reading session."""
        session_id = f"sess_{len(self._sessions) + 1}"
        session = {"id": session_id, "book_id": book_id, "start_time": datetime.utcnow(), **kwargs}
        self._sessions.append(session)
        return {"success": True, "session_id": session_id}

    async def analytics_end_session(self, session_id: str, **kwargs) -> dict:
        """End an active reading session."""
        for session in self._sessions:
            if session.get("id") == session_id and "end_time" not in session:
                session.update({"end_time": datetime.utcnow(), **kwargs})

                # Update reading goals
                self._update_reading_goals(session)

                return {"success": True, "session": session}

        return {"error": "Session not found or already ended", "success": False}

    # Reading Statistics
    async def analytics_get_stats(
        self,
        user_id: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> dict:
        """Get comprehensive reading statistics."""
        sessions = self._filter_sessions(user_id, start_date, end_date)

        if not sessions:
            return {"success": True, "stats": {}}

        # Basic stats
        total_minutes = sum(s.get("duration_minutes", 0) for s in sessions)
        total_books = len({s["book_id"] for s in sessions})
        total_pages = sum(s.get("pages_read", 0) for s in sessions)

        # Reading speed
        speeds = [
            s.get("pages_per_minute") for s in sessions if s.get("pages_per_minute") is not None
        ]

        stats = {
            "total_sessions": len(sessions),
            "total_minutes": total_minutes,
            "total_hours": round(total_minutes / 60, 2),
            "total_books": total_books,
            "total_pages": total_pages,
            "avg_pages_per_session": round(
                statistics.mean(s.get("pages_read", 0) for s in sessions), 2
            )
            if sessions
            else 0,
            "avg_minutes_per_session": round(
                statistics.mean(s.get("duration_minutes", 0) for s in sessions), 2
            )
            if sessions
            else 0,
            "reading_speed": {
                "avg_pages_per_minute": round(statistics.mean(speeds), 2) if speeds else None,
                "median_pages_per_minute": round(statistics.median(speeds), 2) if speeds else None,
                "min_pages_per_minute": round(min(speeds), 2) if speeds else None,
                "max_pages_per_minute": round(max(speeds), 2) if speeds else None,
            },
            "favorite_reading_times": self._calculate_favorite_times(sessions),
            "reading_streak": await self._calculate_reading_streak(user_id),
            "books_completed": await self._count_books_completed(user_id, start_date, end_date),
            "pages_per_day": self._calculate_pages_per_day(sessions, start_date, end_date),
        }

        return {"success": True, "stats": stats}

    # Reading Goals
    async def analytics_create_goal(self, goal_data: dict) -> dict:
        """Create a new reading goal."""
        goal = ReadingGoal(**goal_data)

        # Generate ID if not provided
        if not goal.id:
            goal.id = f"goal_{len(self._goals) + 1}"

        self._goals[goal.id] = goal
        return {"success": True, "goal": goal.dict()}

    async def analytics_update_goal_progress(self, goal_id: str, progress: int) -> dict:
        """Update progress for a reading goal."""
        if goal_id not in self._goals:
            return {"error": f"Goal {goal_id} not found", "success": False}

        goal = self._goals[goal_id]
        goal.update_progress(progress)

        return {"success": True, "goal": goal.dict()}

    async def analytics_get_goals(self, include_completed: bool = True) -> dict:
        """Get all reading goals."""
        goals = [g.dict() for g in self._goals.values() if include_completed or not g.is_completed]

        return {"success": True, "goals": goals}

    # Reading Habits
    async def analytics_reading_habits(self, user_id: str | None = None, days: int = 30) -> dict:
        """Analyze reading habits over time."""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        sessions = self._filter_sessions(user_id, start_date, end_date)

        # Group by date
        daily_stats = defaultdict(lambda: {"minutes": 0, "pages": 0, "sessions": 0})

        for session in sessions:
            date_key = session["start_time"].date().isoformat()
            daily_stats[date_key]["minutes"] += session.get("duration_minutes", 0)
            daily_stats[date_key]["pages"] += session.get("pages_read", 0)
            daily_stats[date_key]["sessions"] += 1

        # Convert to list of daily stats
        result = []
        for i in range(days + 1):
            current_date = (end_date - timedelta(days=i)).date()
            date_key = current_date.isoformat()
            result.append(
                {
                    "date": date_key,
                    "day_of_week": current_date.strftime("%A"),
                    **daily_stats[date_key],
                }
            )

        # Calculate averages
        result.reverse()  # Sort chronologically

        return {
            "success": True,
            "days": result,
            "averages": {
                "daily_minutes": round(statistics.mean(d["minutes"] for d in result), 2),
                "daily_pages": round(statistics.mean(d["pages"] for d in result), 2),
                "daily_sessions": round(statistics.mean(d["sessions"] for d in result), 2),
            },
            "total": {
                "minutes": sum(d["minutes"] for d in result),
                "pages": sum(d["pages"] for d in result),
                "sessions": sum(d["sessions"] for d in result),
            },
            "period": {
                "start_date": start_date.date().isoformat(),
                "end_date": end_date.date().isoformat(),
                "days": days,
            },
        }

    # Helper Methods
    def _filter_sessions(
        self,
        user_id: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[dict]:
        """Filter sessions based on criteria."""
        filtered = self._sessions

        if user_id:
            filtered = [s for s in filtered if s.get("user_id") == user_id]

        if start_date:
            filtered = [s for s in filtered if s["start_time"] >= start_date]

        if end_date:
            filtered = [s for s in filtered if s["start_time"] <= end_date]

        return filtered

    def _calculate_favorite_times(self, sessions: list[dict]) -> dict:
        """Calculate favorite reading times."""
        if not sessions:
            return {}

        # Group by hour of day
        hour_counts = defaultdict(int)
        for session in sessions:
            hour = session["start_time"].hour
            hour_counts[hour] += 1

        # Find top 3 hours
        top_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:3]

        return {
            "top_hours": [{"hour": h, "count": c} for h, c in top_hours],
            "most_common_hour": top_hours[0][0] if top_hours else None,
        }

    async def _calculate_reading_streak(self, user_id: str | None = None) -> dict:
        """Calculate current reading streak in days."""
        sessions = self._filter_sessions(user_id)
        if not sessions:
            return {"days": 0, "start_date": None, "end_date": None}

        # Get unique dates with reading activity
        dates = {s["start_time"].date() for s in sessions}
        dates = sorted(dates, reverse=True)

        # Calculate streak
        streak = 0
        current_date = datetime.utcnow().date()

        for i in range(len(dates)):
            if dates[i] == current_date - timedelta(days=i):
                streak += 1
            else:
                break

        return {
            "days": streak,
            "start_date": dates[0].isoformat() if dates else None,
            "end_date": dates[-1].isoformat() if dates else None,
        }

    async def _count_books_completed(
        self,
        user_id: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> int:
        """Count books marked as completed."""
        # In a real implementation, this would query the database
        # For now, return a mock value
        return 0

    def _calculate_pages_per_day(
        self,
        sessions: list[dict],
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> dict:
        """Calculate pages read per day."""
        if not sessions:
            return {}

        # Group by date
        daily_pages = defaultdict(int)
        for session in sessions:
            date_key = session["start_time"].date().isoformat()
            daily_pages[date_key] += session.get("pages_read", 0)

        # Convert to list of daily stats
        result = [{"date": date, "pages": pages} for date, pages in sorted(daily_pages.items())]

        return {
            "daily": result,
            "average": round(statistics.mean(d["pages"] for d in result), 2) if result else 0,
            "total": sum(d["pages"] for d in result),
        }

    def _update_reading_goals(self, session: dict) -> None:
        """Update reading goals based on session data."""
        for goal in self._goals.values():
            if goal.is_completed:
                continue

            # Update progress based on goal type
            if goal.metric == "pages":
                pages = session.get("pages_read", 0)
                goal.update_progress(goal.current_progress + pages)

            elif goal.metric == "minutes":
                minutes = session.get("duration_minutes", 0)
                goal.update_progress(goal.current_progress + int(minutes))

            elif goal.metric == "books" and session.get("progress_end", 0) >= 0.9:
                # Consider book completed if progress is 90% or more
                goal.update_progress(goal.current_progress + 1)

            # Update daily streak goal
            elif goal.metric == "days":
                # This would be updated by a daily job that checks for reading activity
                pass
