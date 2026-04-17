from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import text

from app.db.session import SessionLocal
from app.services.portfolio_valuation import compute_current_portfolio_value
from ai_engine.data.data_loader import main as run_data_refresh
from ai_engine.features.feature_engineering import main as run_feature_refresh
from ai_engine.forecasting.model import main as run_model_training
from ai_engine.optimization.decision_engine import main as run_decision_engine
from ai_engine.services.portfolio_snapshots import create_portfolio_snapshot

scheduler = BackgroundScheduler()


def run_daily_pipeline_job():
    db = SessionLocal()
    try:
        print("Running daily pipeline job...")

        run_data_refresh()
        run_feature_refresh()
        run_model_training()

        portfolio_rows = db.execute(
            text("SELECT id FROM portfolios ORDER BY id ASC")
        ).fetchall()

        for (portfolio_id,) in portfolio_rows:
            total_value = compute_current_portfolio_value(db, portfolio_id)
            create_portfolio_snapshot(
                db=db,
                portfolio_id=portfolio_id,
                total_value=total_value,
            )

        print("Daily pipeline job completed.")

    finally:
        db.close()


def run_rebalance_for_frequency(frequency: str):
    db = SessionLocal()
    try:
        print(f"Running rebalance job for frequency={frequency}...")

        rows = db.execute(
            text("""
                SELECT p.id
                FROM portfolios p
                LEFT JOIN user_settings us ON us.user_id = p.user_id
                WHERE COALESCE(us.rebalance_frequency, 'weekly') = :frequency
                ORDER BY p.id ASC
            """),
            {"frequency": frequency}
        ).fetchall()

        for (portfolio_id,) in rows:
            run_decision_engine(portfolio_id=portfolio_id)

        print(f"Rebalance job for frequency={frequency} completed.")

    finally:
        db.close()


def start_scheduler():
    if scheduler.running:
        return

    # Daily pipeline every day at 09:00
    scheduler.add_job(
        run_daily_pipeline_job,
        trigger="cron",
        hour=9,
        minute=0,
        id="daily_pipeline_job",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=300,
    )

    # Daily rebalance users every day at 10:00
    scheduler.add_job(
        lambda: run_rebalance_for_frequency("daily"),
        trigger="cron",
        hour=10,
        minute=0,
        id="daily_rebalance_job",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=300,
    )

    # Weekly rebalance users every Monday at 10:00
    scheduler.add_job(
        lambda: run_rebalance_for_frequency("weekly"),
        trigger="cron",
        day_of_week="mon",
        hour=10,
        minute=0,
        id="weekly_rebalance_job",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=300,
    )

    # Monthly rebalance users on day 1 at 10:00
    scheduler.add_job(
        lambda: run_rebalance_for_frequency("monthly"),
        trigger="cron",
        day=1,
        hour=10,
        minute=0,
        id="monthly_rebalance_job",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=300,
    )

    scheduler.start()
    print("Scheduler started.")