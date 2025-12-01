
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from datetime import datetime, timedelta

from shared_python.db.models.usage import UserUsage
from backend.app.models.user import User

class UsageService:
    """Service for managing user token usage and limits."""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def get_or_create_usage(self, user_id: UUID) -> UserUsage:
        """Get the usage record for a user, creating one if it doesn't exist."""
        result = await self.db.execute(select(UserUsage).filter(UserUsage.user_id == user_id))
        usage = result.scalars().first()
        if not usage:
            usage = UserUsage(user_id=user_id)
            self.db.add(usage)
            await self.db.commit()
            await self.db.refresh(usage)
        return usage

    async def check_limits(self, user: User) -> bool:
        """Check if a user has exceeded their daily or monthly budget."""
        usage = await self.get_or_create_usage(user.id)

        # Reset daily/monthly counters if needed
        await self.reset_counters_if_needed(usage)

        if usage.daily_cost >= user.daily_budget:
            usage.daily_budget_exceeded = True
            await self.db.commit()
            return False

        if usage.monthly_cost >= user.monthly_budget:
            usage.monthly_budget_exceeded = True
            await self.db.commit()
            return False

        return True

    async def increment_usage(self, user_id: UUID, cost: float):
        """Increment the usage for a user."""
        usage = await self.get_or_create_usage(user_id)
        usage.daily_cost += cost
        usage.monthly_cost += cost
        usage.daily_requests += 1
        usage.monthly_requests += 1
        await self.db.commit()

    async def reset_counters_if_needed(self, usage: UserUsage):
        """Reset daily and monthly counters if the reset date has passed."""
        now = datetime.utcnow()
        if now.date() > usage.daily_reset_date.date():
            usage.daily_cost = 0.0
            usage.daily_requests = 0
            usage.daily_budget_exceeded = False
            usage.daily_reset_date = now

        if now.month > usage.monthly_reset_date.month or now.year > usage.monthly_reset_date.year:
            usage.monthly_cost = 0.0
            usage.monthly_requests = 0
            usage.monthly_budget_exceeded = False
            usage.monthly_reset_date = now
        
        await self.db.commit()
