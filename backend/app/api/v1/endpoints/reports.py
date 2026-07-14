from fastapi import APIRouter, Depends, HTTPException, status, Header, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import extract
from app.core.database import get_db
from app.models.user import User
from app.models.transaction import Transaction
from app.services.report import report_service
from app.repositories.user import user_repository
from app.services.auth import get_current_user
from app.core.config import settings
import jwt
from datetime import datetime

router = APIRouter()

@router.get("/csv")
def download_csv(
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    actual_token = authorization.split(" ")[1]

    if not actual_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    # 2. Giải mã và kiểm tra token
    try:
        payload = jwt.decode(actual_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Không thể xác thực thông tin đăng nhập."
            )
        user_id = int(user_id_str)
    except (jwt.PyJWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Không thể xác thực thông tin đăng nhập."
        )

    # 3. Lấy thông tin user
    current_user = user_repository.get(db, id=user_id)
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Không tìm thấy người dùng."
        )

    # 4. Tạo file báo cáo và tải về
    csv_file = report_service.export_csv(db, user_id=current_user.id)
    filename = f"aura_finance_report_{current_user.id}.csv"
    return StreamingResponse(
        csv_file,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Type": "text/csv; charset=utf-8"
        }
    )


@router.get("/yearly-summary")
def get_yearly_summary(
    year: int = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Trả về tổng kết tài chính theo năm: thu/chi mỗi tháng, top danh mục chi tiêu/thu nhập."""
    if year is None:
        year = datetime.now().year

    user_id = current_user.id

    # Lấy tất cả giao dịch trong năm
    txs = (
        db.query(Transaction)
        .filter(
            Transaction.user_id == user_id,
            extract("year", Transaction.date) == year
        )
        .all()
    )

    # Tổng hợp theo tháng (dùng float để tránh Decimal + float)
    monthly = {}
    for m in range(1, 13):
        monthly[m] = {"income": 0.0, "expense": 0.0}

    for tx in txs:
        m = tx.date.month
        val = float(tx.amount_base)
        if tx.type == "income":
            monthly[m]["income"] += val
        else:
            monthly[m]["expense"] += val

    monthly_list = [
        {
            "month": m,
            "income": round(monthly[m]["income"], 2),
            "expense": round(monthly[m]["expense"], 2),
            "net": round(monthly[m]["income"] - monthly[m]["expense"], 2)
        }
        for m in range(1, 13)
    ]

    # Tổng cả năm
    total_income = sum(float(tx.amount_base) for tx in txs if tx.type == "income")
    total_expense = sum(float(tx.amount_base) for tx in txs if tx.type == "expense")

    # Top danh mục chi tiêu
    expense_cat: dict[str, float] = {}
    for tx in txs:
        if tx.type == "expense":
            expense_cat[tx.category] = expense_cat.get(tx.category, 0) + float(tx.amount_base)
    top_expense_categories = sorted(
        [{"category": k, "total": round(v, 2)} for k, v in expense_cat.items()],
        key=lambda x: x["total"], reverse=True
    )[:5]

    # Top danh mục thu nhập
    income_cat: dict[str, float] = {}
    for tx in txs:
        if tx.type == "income":
            income_cat[tx.category] = income_cat.get(tx.category, 0) + float(tx.amount_base)
    top_income_categories = sorted(
        [{"category": k, "total": round(v, 2)} for k, v in income_cat.items()],
        key=lambda x: x["total"], reverse=True
    )[:5]

    # Tháng chi nhiều nhất và tháng thu nhiều nhất
    best_income_month = max(monthly_list, key=lambda x: x["income"])
    worst_expense_month = max(monthly_list, key=lambda x: x["expense"])
    best_net_month = max(monthly_list, key=lambda x: x["net"])

    return {
        "year": year,
        "total_income": round(total_income, 2),
        "total_expense": round(total_expense, 2),
        "net_savings": round(total_income - total_expense, 2),
        "total_transactions": len(txs),
        "monthly": monthly_list,
        "top_expense_categories": top_expense_categories,
        "top_income_categories": top_income_categories,
        "best_income_month": best_income_month,
        "worst_expense_month": worst_expense_month,
        "best_net_month": best_net_month,
    }
