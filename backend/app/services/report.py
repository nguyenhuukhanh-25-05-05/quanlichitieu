import csv
import io
from sqlalchemy.orm import Session
from app.repositories.transaction import transaction_repository

class ReportService:
    def export_csv(self, db: Session, user_id: int) -> io.StringIO:
        transactions = transaction_repository.get_by_user(db, user_id=user_id, limit=10000)
        output = io.StringIO()
        
        # UTF-8 BOM to display Vietnamese characters correctly in Excel
        output.write('\ufeff')
        
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow([
            "Mã Giao Dịch", 
            "Thời Gian", 
            "Loại", 
            "Danh Mục", 
            "Số Tiền Gốc", 
            "Đơn Vị Tiền Tệ", 
            "Tỷ Giá Quy Đổi", 
            "Số Tiền Quy Đổi (Base)", 
            "Mô Tả"
        ])
        
        # Write rows
        for tx in transactions:
            writer.writerow([
                tx.id,
                tx.date.strftime("%Y-%m-%d %H:%M:%S") if tx.date else "",
                "Thu nhập" if tx.type == "income" else "Chi tiêu",
                tx.category,
                tx.amount,
                tx.currency,
                tx.exchange_rate,
                tx.amount_base,
                tx.description or ""
            ])
            
        output.seek(0)
        return output

report_service = ReportService()
