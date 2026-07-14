export const round = (num, decimalPlaces) => {
  return parseFloat(num.toFixed(decimalPlaces));
};

export const mockTransactions = [
  {
    id: 101,
    user_id: 0,
    amount: 30000000.0,
    amount_base: 30000000.0,
    type: "income",
    category: "Lương bổng",
    currency: "VND",
    exchange_rate: 1.0,
    description: "Lương tháng 6 chính thức",
    date: new Date().toISOString(),
    created_at: new Date().toISOString()
  },
  {
    id: 102,
    user_id: 0,
    amount: 5500000.0,
    amount_base: 5500000.0,
    type: "income",
    category: "Đầu tư",
    currency: "VND",
    exchange_rate: 1.0,
    description: "Cổ tức quỹ tăng trưởng",
    date: new Date(Date.now() - 86400000 * 2).toISOString(),
    created_at: new Date().toISOString()
  },
  {
    id: 103,
    user_id: 0,
    amount: 6000000.0,
    amount_base: 6000000.0,
    type: "expense",
    category: "Nhà cửa",
    currency: "VND",
    exchange_rate: 1.0,
    description: "Tiền thuê căn hộ chung cư",
    date: new Date(Date.now() - 86400000 * 3).toISOString(),
    created_at: new Date().toISOString()
  },
  {
    id: 104,
    user_id: 0,
    amount: 450000.0,
    amount_base: 450000.0,
    type: "expense",
    category: "Ăn uống",
    currency: "VND",
    exchange_rate: 1.0,
    description: "Lẩu Kichi Kichi cùng nhóm bạn",
    date: new Date(Date.now() - 86400000 * 4).toISOString(),
    created_at: new Date().toISOString()
  },
  {
    id: 105,
    user_id: 0,
    amount: 260000.0,
    amount_base: 260000.0,
    type: "expense",
    category: "Giải trí",
    currency: "VND",
    exchange_rate: 1.0,
    description: "Gói đăng ký Netflix Premium",
    date: new Date(Date.now() - 86400000 * 5).toISOString(),
    created_at: new Date().toISOString()
  },
  {
    id: 106,
    user_id: 0,
    amount: 1200000.0,
    amount_base: 1200000.0,
    type: "expense",
    category: "Mua sắm",
    currency: "VND",
    exchange_rate: 1.0,
    description: "Mua giày thể thao mới",
    date: new Date(Date.now() - 86400000 * 6).toISOString(),
    created_at: new Date().toISOString()
  },
  {
    id: 107,
    user_id: 0,
    amount: 150000.0,
    amount_base: 150000.0,
    type: "expense",
    category: "Di chuyển",
    currency: "VND",
    exchange_rate: 1.0,
    description: "Nạp tiền xăng xe di chuyển",
    date: new Date(Date.now() - 86400000 * 7).toISOString(),
    created_at: new Date().toISOString()
  }
];

export const calculateMockSummary = (txs) => {
  let totalIncome = 0;
  let totalExpense = 0;
  const categoryExpenses = {};
  const categoryIncomes = {};
  
  txs.forEach(t => {
    if (t.type === 'income') {
      totalIncome += t.amount_base;
      categoryIncomes[t.category] = (categoryIncomes[t.category] || 0) + t.amount_base;
    } else {
      totalExpense += t.amount_base;
      categoryExpenses[t.category] = (categoryExpenses[t.category] || 0) + t.amount_base;
    }
  });

  const expenseStats = Object.keys(categoryExpenses).map(cat => {
    const total = categoryExpenses[cat];
    const pct = totalExpense > 0 ? (total / totalExpense * 100) : 0;
    return { category: cat, total, percentage: round(pct, 2) };
  }).sort((a, b) => b.total - a.total);

  const incomeStats = Object.keys(categoryIncomes).map(cat => {
    const total = categoryIncomes[cat];
    const pct = totalIncome > 0 ? (total / totalIncome * 100) : 0;
    return { category: cat, total, percentage: round(pct, 2) };
  }).sort((a, b) => b.total - a.total);

  return {
    total_income: totalIncome,
    total_expense: totalExpense,
    balance: 23140000.0 + totalIncome - totalExpense,
    category_expenses: expenseStats,
    category_incomes: incomeStats
  };
};

export const generateMockInsights = (summary) => {
  const insights = [];
  const spendRatio = (summary.total_expense / summary.total_income * 100);
  
  if (spendRatio > 90) {
    insights.push(`**Cảnh báo Nguy cấp**: Bạn đã chi tiêu đến **${spendRatio.toFixed(1)}%** tổng thu nhập của mình. Hãy cân nhắc cắt giảm chi tiêu.`);
  } else if (spendRatio > 70) {
    insights.push(`**Nhận xét**: Chi tiêu chiếm **${spendRatio.toFixed(1)}%** thu nhập. Mức chi tiêu này tương đối cao, cần thắt chặt ngân sách.`);
  } else {
    insights.push(`**Khen ngợi**: Tỷ lệ tích lũy tốt! Bạn mới chi tiêu **${spendRatio.toFixed(1)}%** thu nhập, phần còn lại được lưu trữ làm số dư khả dụng.`);
  }
  
  const foodPct = summary.category_expenses.find(x => x.category === 'Ăn uống')?.percentage || 0;
  if (foodPct > 30) {
    insights.push(`**Ăn uống chiếm tỷ trọng lớn**: Chi phí ăn uống chiếm tới **${foodPct}%** tổng chi tiêu. Hãy thử nấu ăn ở nhà để tiết kiệm.`);
  } else {
    insights.push(`**Ăn uống hợp lý**: Chi phí ăn uống chiếm **${foodPct}%** tổng chi tiêu. Đây là mức kiểm soát tốt.`);
  }
  
  insights.push("**Mẹo**: Bạn có 2 giao dịch định kỳ sắp tới (Netflix, Tiền mạng). Hãy chuẩn bị khoảng **480,000 VND** cho các dịch vụ này.");
  return insights;
};

export const mockBudgets = [
  {
    budget: {
      id: 201,
      user_id: 0,
      category: "Ăn uống",
      amount_limit: 5000000.0,
      current_spend: 450000.0,
      period: "monthly",
      start_date: new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString(),
      end_date: new Date(new Date().getFullYear(), new Date().getMonth() + 1, 0).toISOString(),
      created_at: new Date().toISOString()
    },
    percent_used: 9.0,
    is_exceeded: false
  },
  {
    budget: {
      id: 202,
      user_id: 0,
      category: "Mua sắm",
      amount_limit: 1000000.0,
      current_spend: 1200000.0,
      period: "monthly",
      start_date: new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString(),
      end_date: new Date(new Date().getFullYear(), new Date().getMonth() + 1, 0).toISOString(),
      created_at: new Date().toISOString()
    },
    percent_used: 120.0,
    is_exceeded: true
  },
  {
    budget: {
      id: 203,
      user_id: 0,
      category: "Di chuyển",
      amount_limit: 500000.0,
      current_spend: 150000.0,
      period: "monthly",
      start_date: new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString(),
      end_date: new Date(new Date().getFullYear(), new Date().getMonth() + 1, 0).toISOString(),
      created_at: new Date().toISOString()
    },
    percent_used: 30.0,
    is_exceeded: false
  }
];

export const mockRecurrings = [
  {
    id: 301,
    user_id: 0,
    amount: 260000.0,
    type: "expense",
    category: "Giải trí",
    currency: "VND",
    description: "Đăng ký gói Netflix Premium",
    frequency: "monthly",
    next_run_date: new Date(Date.now() + 86400000 * 5).toISOString(),
    is_active: true,
    created_at: new Date().toISOString()
  },
  {
    id: 302,
    user_id: 0,
    amount: 220000.0,
    type: "expense",
    category: "Nhà cửa",
    currency: "VND",
    description: "Cước thuê bao mạng FPT",
    frequency: "monthly",
    next_run_date: new Date(Date.now() + 86400000 * 12).toISOString(),
    is_active: true,
    created_at: new Date().toISOString()
  }
];
