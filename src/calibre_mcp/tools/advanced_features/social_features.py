"""Social features for CalibreMCP."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, HttpUrl

try:
    from fastmcp import MCPTool
except ImportError:
    from ..compat import MCPTool


# Models
class UserProfile(BaseModel):
    """User profile for social features."""

    user_id: str
    username: str
    display_name: str
    avatar_url: HttpUrl | None = None
    bio: str | None = None
    location: str | None = None
    website: HttpUrl | None = None
    reading_goals: dict[str, Any] = Field(default_factory=dict)
    reading_stats: dict[str, Any] = Field(default_factory=dict)
    privacy_settings: dict[str, bool] = Field(
        default_factory=lambda: {
            "profile_public": True,
            "reading_activity_public": True,
            "reviews_public": True,
            "followers_public": True,
            "following_public": True,
        }
    )
    social_links: dict[str, str] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            HttpUrl: lambda v: str(v) if v else None,
        }

    def update_timestamp(self):
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()


class BookReview(BaseModel):
    """A book review by a user."""

    id: str
    book_id: str
    user_id: str
    rating: float = Field(..., ge=0, le=5)
    title: str
    content: str
    is_public: bool = True
    likes: int = 0
    liked_by: list[str] = Field(default_factory=list)  # List of user IDs
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat() if v else None}

    def update_content(self, content: str, title: str | None = None):
        """Update review content and title."""
        self.content = content
        if title is not None:
            self.title = title
        self.updated_at = datetime.utcnow()

    def add_like(self, user_id: str) -> bool:
        """Add a like from a user."""
        if user_id not in self.liked_by:
            self.liked_by.append(user_id)
            self.likes = len(self.liked_by)
            return True
        return False

    def remove_like(self, user_id: str) -> bool:
        """Remove a like from a user."""
        if user_id in self.liked_by:
            self.liked_by.remove(user_id)
            self.likes = len(self.liked_by)
            return True
        return False


class ReadingList(BaseModel):
    """A curated list of books."""

    id: str
    creator_id: str
    title: str
    description: str | None = None
    book_ids: list[str] = Field(default_factory=list)
    is_public: bool = True
    is_collaborative: bool = False
    collaborators: list[str] = Field(default_factory=list)  # List of user IDs
    tags: list[str] = Field(default_factory=list)
    cover_image: HttpUrl | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            HttpUrl: lambda v: str(v) if v else None,
        }

    def add_book(self, book_id: str) -> bool:
        """Add a book to the list if not already present."""
        if book_id not in self.book_ids:
            self.book_ids.append(book_id)
            self.updated_at = datetime.utcnow()
            return True
        return False

    def remove_book(self, book_id: str) -> bool:
        """Remove a book from the list."""
        if book_id in self.book_ids:
            self.book_ids.remove(book_id)
            self.updated_at = datetime.utcnow()
            return True
        return False

    def add_collaborator(self, user_id: str) -> bool:
        """Add a collaborator to the list."""
        if user_id not in self.collaborators and user_id != self.creator_id:
            self.collaborators.append(user_id)
            self.updated_at = datetime.utcnow()
            return True
        return False

    def remove_collaborator(self, user_id: str) -> bool:
        """Remove a collaborator from the list."""
        if user_id in self.collaborators:
            self.collaborators.remove(user_id)
            self.updated_at = datetime.utcnow()
            return True
        return False


# Main tool
class SocialFeaturesTool(MCPTool):
    """Social features for CalibreMCP."""

    name = "social_features"
    description = "Social features including reviews, reading lists, and user interactions"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._profiles = {}  # user_id -> UserProfile
        self._reviews = {}  # review_id -> BookReview
        self._reading_lists = {}  # list_id -> ReadingList
        self._follows = {}  # user_id -> Set[user_id] (who they follow)
        self._followers = {}  # user_id -> Set[user_id] (who follows them)
        self._notifications = {}  # user_id -> List[Notification]

    async def _run(self, action: str, **kwargs) -> dict:
        """Route to the appropriate social feature handler."""
        handler = getattr(self, f"social_{action}", None)
        if not handler:
            return {"error": f"Unknown social action: {action}", "success": False}

        try:
            return await handler(**kwargs)
        except Exception as e:
            return {"error": str(e), "success": False}

    # User Profiles
    async def social_create_profile(
        self, user_id: str, username: str, display_name: str, **kwargs
    ) -> dict:
        """Create a new user profile."""
        if user_id in self._profiles:
            return {"error": f"Profile for user {user_id} already exists", "success": False}

        # Check if username is taken
        if any(p.username.lower() == username.lower() for p in self._profiles.values()):
            return {"error": f"Username '{username}' is already taken", "success": False}

        profile = UserProfile(
            user_id=user_id, username=username, display_name=display_name, **kwargs
        )

        self._profiles[user_id] = profile

        # Initialize follow data structures
        self._follows[user_id] = set()
        self._followers[user_id] = set()
        self._notifications[user_id] = []

        return {"success": True, "profile": profile.dict()}

    async def social_get_profile(self, user_id: str) -> dict:
        """Get a user's profile."""
        if user_id not in self._profiles:
            return {"error": f"Profile for user {user_id} not found", "success": False}

        profile = self._profiles[user_id]
        return {"success": True, "profile": profile.dict()}

    async def social_update_profile(self, user_id: str, updates: dict[str, Any]) -> dict:
        """Update a user's profile."""
        if user_id not in self._profiles:
            return {"error": f"Profile for user {user_id} not found", "success": False}

        profile = self._profiles[user_id]

        # Update fields
        for field, value in updates.items():
            if hasattr(profile, field) and field not in ["user_id", "created_at"]:
                setattr(profile, field, value)

        profile.updated_at = datetime.utcnow()

        return {"success": True, "profile": profile.dict()}

    # Reviews
    async def social_create_review(
        self, book_id: str, user_id: str, rating: float, title: str, content: str
    ) -> dict:
        """Create a new book review."""
        # Check if user has already reviewed this book
        existing_review = next(
            (r for r in self._reviews.values() if r.book_id == book_id and r.user_id == user_id),
            None,
        )

        if existing_review:
            return {
                "error": "You have already reviewed this book. Please update your existing review.",
                "success": False,
                "review_id": existing_review.id,
            }

        review_id = f"rev_{len(self._reviews) + 1}"
        review = BookReview(
            id=review_id,
            book_id=book_id,
            user_id=user_id,
            rating=rating,
            title=title,
            content=content,
        )

        self._reviews[review_id] = review

        return {"success": True, "review": review.dict()}

    async def social_get_review(self, review_id: str) -> dict:
        """Get a book review by ID."""
        if review_id not in self._reviews:
            return {"error": f"Review {review_id} not found", "success": False}

        return {"success": True, "review": self._reviews[review_id].dict()}

    async def social_get_book_reviews(
        self, book_id: str, sort_by: str = "newest", limit: int = 10, offset: int = 0
    ) -> dict:
        """Get reviews for a book."""
        reviews = [r for r in self._reviews.values() if r.book_id == book_id and r.is_public]

        # Sort
        if sort_by == "newest":
            reviews.sort(key=lambda x: x.created_at, reverse=True)
        elif sort_by == "highest_rated":
            reviews.sort(key=lambda x: x.rating, reverse=True)
        elif sort_by == "most_liked":
            reviews.sort(key=lambda x: x.likes, reverse=True)

        # Paginate
        paginated = reviews[offset : offset + limit]

        return {
            "success": True,
            "book_id": book_id,
            "total_reviews": len(reviews),
            "reviews": [r.dict() for r in paginated],
            "pagination": {
                "offset": offset,
                "limit": limit,
                "has_more": (offset + len(paginated)) < len(reviews),
            },
        }

    # Reading Lists
    async def social_create_reading_list(
        self, creator_id: str, title: str, description: str | None = None, is_public: bool = True
    ) -> dict:
        """Create a new reading list."""
        list_id = f"rl_{len(self._reading_lists) + 1}"
        reading_list = ReadingList(
            id=list_id,
            creator_id=creator_id,
            title=title,
            description=description,
            is_public=is_public,
        )

        self._reading_lists[list_id] = reading_list

        return {"success": True, "reading_list": reading_list.dict()}

    async def social_get_reading_list(self, list_id: str) -> dict:
        """Get a reading list by ID."""
        if list_id not in self._reading_lists:
            return {"error": f"Reading list {list_id} not found", "success": False}

        return {"success": True, "reading_list": self._reading_lists[list_id].dict()}

    async def social_get_estimated_reading_time(self, book_id: str) -> dict:
        """Get the estimated reading time for a book."""
        # For now, return a mock value
        return {
            "success": True,
            "reading_time_minutes": 120,
            "message": "[SIMULATED] Estimated reading time",
        }

    async def social_search_reading_lists(
        self,
        query: str | None = None,
        tags: list[str] | None = None,
        user_id: str | None = None,
        limit: int = 10,
        offset: int = 0,
    ) -> dict:
        """Search for reading lists."""
        results = []

        for rl in self._reading_lists.values():
            # Skip private lists unless owned by the user
            if not rl.is_public and rl.creator_id != user_id:
                continue

            # Filter by user if specified
            if user_id and rl.creator_id != user_id:
                continue

            # Filter by query
            if (
                query
                and query.lower() not in rl.title.lower()
                and (not rl.description or query.lower() not in rl.description.lower())
            ):
                continue

            # Filter by tags if specified
            if tags and not any(tag in rl.tags for tag in tags):
                continue

            results.append(rl)

        # Sort by most recently updated
        results.sort(key=lambda x: x.updated_at, reverse=True)

        # Paginate
        paginated = results[offset : offset + limit]

        return {
            "success": True,
            "total_lists": len(results),
            "lists": [r.dict() for r in paginated],
            "pagination": {
                "offset": offset,
                "limit": limit,
                "has_more": (offset + len(paginated)) < len(results),
            },
        }

    # Following/Followers
    async def social_follow_user(self, follower_id: str, followed_id: str) -> dict:
        """Follow a user."""
        if follower_id == followed_id:
            return {"error": "You cannot follow yourself", "success": False}

        if follower_id not in self._profiles or followed_id not in self._profiles:
            return {"error": "User not found", "success": False}

        # Add to follows
        if follower_id not in self._follows:
            self._follows[follower_id] = set()
        self._follows[follower_id].add(followed_id)

        # Add to followers
        if followed_id not in self._followers:
            self._followers[followed_id] = set()
        self._followers[followed_id].add(follower_id)

        # Create notification
        await self._create_notification(
            user_id=followed_id,
            type="new_follower",
            data={"follower_id": follower_id},
            from_user_id=follower_id,
        )

        return {
            "success": True,
            "follower_id": follower_id,
            "followed_id": followed_id,
            "following": True,
        }

    async def social_unfollow_user(self, follower_id: str, followed_id: str) -> dict:
        """Unfollow a user."""
        if follower_id == followed_id:
            return {"error": "Invalid operation", "success": False}

        # Remove from follows
        if follower_id in self._follows and followed_id in self._follows[follower_id]:
            self._follows[follower_id].remove(followed_id)

        # Remove from followers
        if followed_id in self._followers and follower_id in self._followers[followed_id]:
            self._followers[followed_id].remove(follower_id)

        return {
            "success": True,
            "follower_id": follower_id,
            "followed_id": followed_id,
            "following": False,
        }

    async def social_get_followers(self, user_id: str) -> dict:
        """Get a user's followers."""
        if user_id not in self._profiles:
            return {"error": "User not found", "success": False}

        followers = list(self._followers.get(user_id, set()))

        return {
            "success": True,
            "user_id": user_id,
            "followers": followers,
            "count": len(followers),
        }

    async def social_get_following(self, user_id: str) -> dict:
        """Get users that a user is following."""
        if user_id not in self._profiles:
            return {"error": "User not found", "success": False}

        following = list(self._follows.get(user_id, set()))

        return {
            "success": True,
            "user_id": user_id,
            "following": following,
            "count": len(following),
        }

    # Notifications
    async def social_get_notifications(
        self, user_id: str, unread_only: bool = True, limit: int = 20
    ) -> dict:
        """Get notifications for a user."""
        if user_id not in self._notifications:
            return {"success": True, "notifications": [], "unread_count": 0}

        notifications = self._notifications[user_id]

        if unread_only:
            notifications = [n for n in notifications if not n.get("read")]

        # Sort by most recent
        notifications.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

        # Apply limit
        notifications = notifications[:limit]

        # Mark as read if needed
        if not unread_only:
            for n in notifications:
                if not n.get("read"):
                    n["read"] = True

        return {
            "success": True,
            "notifications": notifications,
            "unread_count": sum(1 for n in self._notifications[user_id] if not n.get("read")),
        }

    # Helper Methods
    async def _create_notification(
        self, user_id: str, type: str, data: dict, from_user_id: str | None = None
    ):
        """Create a new notification for a user."""
        if user_id not in self._notifications:
            self._notifications[user_id] = []

        notification = {
            "id": f"notif_{len(self._notifications[user_id]) + 1}",
            "type": type,
            "data": data,
            "from_user_id": from_user_id,
            "read": False,
            "timestamp": datetime.utcnow().isoformat(),
        }

        self._notifications[user_id].append(notification)

        # Keep only the most recent 100 notifications per user
        self._notifications[user_id] = self._notifications[user_id][-100:]

        return notification

    # Activity Feed
    async def social_get_activity_feed(
        self, user_id: str, limit: int = 20, offset: int = 0
    ) -> dict:
        """Get a user's activity feed."""
        if user_id not in self._profiles:
            return {"error": "User not found", "success": False}

        # In a real implementation, this would aggregate activities from:
        # - Users the current user follows
        # - Public activities from the community
        # - Popular/recommended content

        # For now, return a mock response
        activities = []

        return {
            "success": True,
            "activities": activities,
            "pagination": {"offset": offset, "limit": limit, "has_more": False},
        }

    # Book Clubs
    async def social_create_book_club(
        self, creator_id: str, name: str, description: str, is_public: bool = True
    ) -> dict:
        """Create a new book club."""
        # In a real implementation, this would create a book club
        # For now, return a mock response

        book_club_id = f"bc_{len(self._reading_lists) + 1}"

        return {
            "success": True,
            "book_club": {
                "id": book_club_id,
                "name": name,
                "description": description,
                "creator_id": creator_id,
                "is_public": is_public,
                "members": [creator_id],
                "created_at": datetime.utcnow().isoformat(),
            },
        }

    async def social_join_book_club(self, user_id: str, club_id: str) -> dict:
        """Join a book club."""
        # In a real implementation, this would add the user to the club
        # For now, return a mock response

        return {
            "success": True,
            "club_id": club_id,
            "user_id": user_id,
            "joined": True,
            "message": "Successfully joined the book club",
        }

    # Reading Challenges
    async def social_create_reading_challenge(
        self,
        creator_id: str,
        name: str,
        description: str,
        target_books: int,
        start_date: str,
        end_date: str,
        is_public: bool = True,
    ) -> dict:
        """Create a new reading challenge."""
        # In a real implementation, this would create a reading challenge
        # For now, return a mock response

        challenge_id = f"rc_{len(self._reading_lists) + 1}"

        return {
            "success": True,
            "challenge": {
                "id": challenge_id,
                "name": name,
                "description": description,
                "creator_id": creator_id,
                "target_books": target_books,
                "start_date": start_date,
                "end_date": end_date,
                "is_public": is_public,
                "participants": [creator_id],
                "created_at": datetime.utcnow().isoformat(),
            },
        }

    async def social_join_reading_challenge(self, user_id: str, challenge_id: str) -> dict:
        """Join a reading challenge."""
        # In a real implementation, this would add the user to the challenge
        # For now, return a mock response

        return {
            "success": True,
            "challenge_id": challenge_id,
            "user_id": user_id,
            "joined": True,
            "message": "Successfully joined the reading challenge",
        }
