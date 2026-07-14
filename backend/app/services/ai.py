from sqlalchemy.orm import Session
from app.repositories.transaction import transaction_repository
from app.repositories.budget import budget_repository

class AIService:
    def get_financial_insights(self, db: Session, user_id: int) -> list[str]:
        insights = []
        
        total_income, total_expense = transaction_repository.get_user_totals(db, user_id=user_id)
        expense_cats = transaction_repository.get_category_sums(db, user_id=user_id, type="expense")
        budgets = budget_repository.get_by_user(db, user_id=user_id)

        # 1. Total spending ratio warning
        if total_income > 0:
            spend_ratio = (total_expense / total_income) * 100
            if spend_ratio > 90:
                insights.append(
                    f"**Cảnh báo Nguy cấp**: Bạn đã chi tiêu đến **{spend_ratio:.1f}%** tổng thu nhập của mình. Hãy cân nhắc cắt giảm các khoản chi không thiết yếu ngay lập tức."
                )
            elif spend_ratio > 75:
                insights.append(
                    f"**Nhận xét**: Chi tiêu chiếm **{spend_ratio:.1f}%** thu nhập. Bạn chỉ còn lưu trữ được một phần nhỏ để tiết kiệm. Bạn nên đặt hạn mức chi tiêu chặt chẽ hơn."
                )
            else:
                insights.append(
                    f"**Khen ngợi**: Tỷ lệ tích lũy của bạn rất tốt! Bạn mới chi tiêu **{spend_ratio:.1f}%** thu nhập, phần còn lại có thể đưa vào quỹ đầu tư hoặc tiết kiệm."
                )
        elif total_expense > 0:
            insights.append(
                "**Lưu ý**: Bạn ghi nhận các khoản chi nhưng chưa có thu nhập. Hãy bổ sung nguồn thu để có cái nhìn chính xác hơn về sức khỏe tài chính."
            )

        # 2. Category specific analysis
        food_expense = next((amount for cat, amount in expense_cats if cat.lower() in ["food", "ăn uống", "an uong"]), 0.0)
        if total_expense > 0 and food_expense > 0:
            food_ratio = (food_expense / total_expense) * 100
            if food_ratio > 35:
                insights.append(
                    f"**Ăn uống chiếm tỷ trọng lớn**: Chi phí ăn uống chiếm tới **{food_ratio:.1f}%** tổng chi tiêu của bạn. Việc tự chuẩn bị bữa ăn tại nhà có thể giúp bạn tiết kiệm một khoản kha khá đấy!"
                )

        # 3. Budget warnings
        exceeded_budgets = [b for b in budgets if b.current_spend >= b.amount_limit]
        if exceeded_budgets:
            categories_str = ", ".join([f"&apos;{b.category}&apos;" for b in exceeded_budgets])
            insights.append(
                f"**Hạn mức chi tiêu bị phá vỡ**: Bạn đã vượt quá ngân sách đặt ra cho các danh mục: {categories_str}. Hãy kiểm tra lại danh sách chi tiêu để xem có khoản nào bất thường không."
            )
        
        # 4. Standard suggestions if no logs
        if not insights:
            insights.append("**Gợi ý**: Hãy bắt đầu bằng cách thêm các khoản thu nhập và chi tiêu hàng ngày để nhận được phân tích tài chính chi tiết nhất từ trợ lý AuraFinance.")

        return insights

ai_service = AIService()
