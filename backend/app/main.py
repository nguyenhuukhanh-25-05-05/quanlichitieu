import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import asyncio
import httpx
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)

from app.core.config import settings
from app.core.database import engine, SessionLocal
from app.models import Base
from app.api.v1.api import api_router
from app.repositories.recurring import recurring_repository
from app.schemas.transaction import TransactionCreate
from app.services.transaction import transaction_service

# Lifespan context manager for startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create database tables
    Base.metadata.create_all(bind=engine)
    
    # Seed demo data for development only
    if settings.ENVIRONMENT == "development":
        db = SessionLocal()
        try:
            from app.models.user import User
            from app.models.transaction import Transaction
            from app.models.budget import Budget
            from app.models.recurring import RecurringTransaction
            from app.core.security import get_password_hash
            
            demo_email = "demo@aurafinance.app"
            user = db.query(User).filter(User.email == demo_email).first()
            if not user:
                import logging
                logger = logging.getLogger(__name__)
                logger.info("Seeding demo user data")
                
                user = User(
                    email=demo_email,
                    hashed_password=get_password_hash("123456"),
                    fullname="Nhà Tuyển Dụng",
                    currency="VND",
                    balance=46900000.0
                )
                db.add(user)
                db.commit()
                db.refresh(user)

            # Seed transactions
            transactions = [
                Transaction(user_id=user.id, amount=45000000.0, type="income", category="Lương bổng", currency="VND", exchange_rate=1.0, amount_base=45000000.0, description="Lương dự án Công nghệ Phần mềm Công ty ABC", date=datetime.now(timezone.utc) - timedelta(days=2)),
                Transaction(user_id=user.id, amount=12500000.0, type="income", category="Đầu tư", currency="VND", exchange_rate=1.0, amount_base=12500000.0, description="Cổ tức định kỳ từ quỹ đầu tư VN30 ETF", date=datetime.now(timezone.utc) - timedelta(days=7)),
                Transaction(user_id=user.id, amount=8000000.0, type="income", category="Làm thêm", currency="VND", exchange_rate=1.0, amount_base=8000000.0, description="Dự án Freelance thiết kế UI/UX Landing Page", date=datetime.now(timezone.utc) - timedelta(days=12)),
                
                Transaction(user_id=user.id, amount=5400000.0, type="expense", category="Nhà cửa", currency="VND", exchange_rate=1.0, amount_base=5400000.0, description="Thanh toán hóa đơn điện nước & Internet gia đình", date=datetime.now(timezone.utc) - timedelta(days=1)),
                Transaction(user_id=user.id, amount=3200000.0, type="expense", category="Mua sắm", currency="VND", exchange_rate=1.0, amount_base=3200000.0, description="Chi phí mua sắm thiết bị văn phòng (Bàn phím cơ)", date=datetime.now(timezone.utc) - timedelta(days=3)),
                Transaction(user_id=user.id, amount=1850000.0, type="expense", category="Ăn uống", currency="VND", exchange_rate=1.0, amount_base=1850000.0, description="Chi tiêu ăn uống & tiếp đối tác dự án", date=datetime.now(timezone.utc) - timedelta(days=5)),
                Transaction(user_id=user.id, amount=2450000.0, type="expense", category="Di chuyển", currency="VND", exchange_rate=1.0, amount_base=2450000.0, description="Chi phí bảo dưỡng xe máy định kỳ", date=datetime.now(timezone.utc) - timedelta(days=9)),
                Transaction(user_id=user.id, amount=4500000.0, type="expense", category="Giải trí", currency="VND", exchange_rate=1.0, amount_base=4500000.0, description="Đăng ký khóa học phát triển bản thân trực tuyến", date=datetime.now(timezone.utc) - timedelta(days=17)),
                Transaction(user_id=user.id, amount=1200000.0, type="expense", category="Y tế", currency="VND", exchange_rate=1.0, amount_base=1200000.0, description="Mua gói bảo hiểm sức khỏe định kỳ", date=datetime.now(timezone.utc) - timedelta(days=22)),
            ]
            db.add_all(transactions)

            # Seed budgets
            budgets = [
                Budget(user_id=user.id, category="Ăn uống", amount_limit=5000000.0, current_spend=1850000.0, start_date=datetime.now(timezone.utc) - timedelta(days=26), end_date=datetime.now(timezone.utc) + timedelta(days=4), period="monthly"),
                Budget(user_id=user.id, category="Mua sắm", amount_limit=8000000.0, current_spend=3200000.0, start_date=datetime.now(timezone.utc) - timedelta(days=26), end_date=datetime.now(timezone.utc) + timedelta(days=4), period="monthly"),
            ]
            db.add_all(budgets)

            # Seed recurring transactions
            recurrings = [
                RecurringTransaction(user_id=user.id, amount=5400000.0, type="expense", category="Nhà cửa", currency="VND", frequency="monthly", next_run_date=datetime.now(timezone.utc) + timedelta(days=8), description="Thanh toán hóa đơn điện nước & Internet gia đình", is_active=True),
                RecurringTransaction(user_id=user.id, amount=45000000.0, type="income", category="Lương bổng", currency="VND", frequency="monthly", next_run_date=datetime.now(timezone.utc) + timedelta(days=28), description="Lương dự án Công nghệ Phần mềm Công ty ABC", is_active=True),
            ]
            db.add_all(recurrings)
            db.commit()
        except Exception:
            import logging
            logger = logging.getLogger(__name__)
            logger.exception("Failed to seed demo data")
            db.rollback()
        finally:
            db.close()

    # Start the background scheduler for recurring transactions
    bg_task = asyncio.create_task(recurring_transactions_worker())
    
    yield
    
    # Shutdown: Cancel the background task
    bg_task.cancel()
    try:
        await bg_task
    except asyncio.CancelledError:
        pass

# Background worker that checks and processes recurring transactions
async def recurring_transactions_worker():
    while True:
        try:
            await asyncio.sleep(300)
            db = SessionLocal()
            try:
                due_recurrings = recurring_repository.get_active_due(db)
                for rec in due_recurrings:
                    # Create the transaction
                    tx_in = TransactionCreate(
                        amount=rec.amount,
                        type=rec.type,
                        category=rec.category,
                        currency=rec.currency,
                        exchange_rate=1.0,
                        description=f"[Tự động] {rec.description or ''}",
                        date=datetime.now(timezone.utc)
                    )
                    # Run the create transaction service (this updates balance and checks budget)
                    await transaction_service.create_transaction(db, user_id=rec.user_id, transaction_in=tx_in)
                    
                    # Update next run date based on frequency
                    next_run = rec.next_run_date
                    if rec.frequency == "daily":
                        next_run += timedelta(days=1)
                    elif rec.frequency == "weekly":
                        next_run += timedelta(weeks=1)
                    elif rec.frequency == "monthly":
                        next_run += timedelta(days=30)
                    
                    recurring_repository.update(db, db_obj=rec, obj_in={"next_run_date": next_run})
            finally:
                db.close()
        except asyncio.CancelledError:
            break
        except Exception as e:
            import logging
            logging.exception("Recurring transaction worker error: %s", e)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "Idempotency-Key"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = datetime.now(timezone.utc)
    response = await call_next(request)
    duration = (datetime.now(timezone.utc) - start).total_seconds()
    logger.info(
        "%s %s %s %.3fs",
        request.method, request.url.path, response.status_code, duration
    )
    return response

# Include API Router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to AuraFinance API",
        "docs": "/docs",
        "version": settings.VERSION
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }


