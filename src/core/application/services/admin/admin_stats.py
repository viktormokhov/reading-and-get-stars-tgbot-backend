from sqlalchemy import func, select

from core.domain.models.stats import GeneralStats
from core.domain.services.users.user_progress import get_status_by_stars
from core.infrastructure.db.models import UserStars, User


async def get_general_stats(user_repo) -> GeneralStats:
    users = await user_repo.select_where(lambda u: True).scalars().all()
    # async with AsyncSessionLocal() as s:
    # users = (await s.execute(user_ops.select_users_where(lambda u: True))).scalars().all()
    total = len(users)
    approved = sum(1 for u in users if u.is_approved)
    avg_acc = (sum((u.q_ok / u.q_tot if u.q_tot else 0) for u in users) / total) if total else 0

    # Calculate total stars from UserStar table
    total_stars_result = await s.execute(select(func.sum(UserStars.count)))
    total_stars = total_stars_result.scalar() or 0

    total_active_seconds = sum(
        ((u.last_active - u.first_active).total_seconds() if u.first_active and u.last_active else 0)
        for u in users
    )
    avg_active_seconds = total_active_seconds / total if total else 0

    total_questions = (await s.execute(func.sum(ThemeStat.texts))).scalar() or 0
    total_cards = (await s.execute(func.count(UserCards.id))).scalar() or 0

    hours = int(avg_active_seconds // 3600)
    minutes = int((avg_active_seconds % 3600) // 60)

    return GeneralStats(
        total_users=total,
        approved_users=approved,
        avg_accuracy=avg_acc,
        total_stars=total_stars,
        avg_active_hours=hours,
        avg_active_minutes=minutes,
        total_questions=total_questions,
        total_cards=total_cards,
    )


async def render_user_stats(user_id: int) -> tuple[str, User | None]:
    """Возвращает форматированную инфо о пользователе и объект User."""
    async with AsyncSessionLocal() as s:
        user = await s.get(User, user_id)
        if not user:
            return "❌ Пользователь не найден.", None

        result = await s.execute(user_ops.select_user_theme_stats(user_id))
        themes = {t.theme: t.texts for t in result.scalars().all()}

        # Get stars count from UserStar table
        stars = await get_user_stars_count(user_id, s)

    q_ok = user.q_ok or 0
    q_tot = user.q_tot or 0
    streak = user.streak or 0
    acc = f"{(q_ok / q_tot * 100):.0f}%" if q_tot else "—"
    status = "✅" if user.is_approved else "⏳"
    badge = get_status_by_stars(stars)

    lines = [
        f"{status} <b>{user.name}</b> (ID: <code>{user.id}</code>)",
        f"<b>Статус</b>: {badge}\n"
        f"<b>Звездочки</b>: ⭐ {stars}\n"
        f"<b>Правильных ответов</b>: ✔️ {q_ok}\n"
        f"<b>Точность</b>: 🎯 {acc}\n"
        f"<b>Стрики</b>:🔥 {streak}"
    ]

    if themes:
        lines += ["────────────────────────────", "📚 <b>По темам</b>:"]
        lines += [f"• {theme}: {count}" for theme, count in themes.items()]

    return "\n".join(lines), user
