export const categories = {
  expense: [
    'Ăn uống', 'Mua sắm', 'Di chuyển', 'Nhà cửa',
    'Giải trí', 'Y tế', 'Giáo dục', 'Hoá đơn & Tiện ích',
    'Bảo hiểm', 'Du lịch', 'Quà tặng & Từ thiện', 'Khác'
  ],
  income: [
    'Lương bổng', 'Đầu tư', 'Kinh doanh', 'Lãi tiết kiệm',
    'Quà tặng', 'Thu nhập thụ động', 'Khác'
  ]
};

export function getCategoryClass(category) {
  const map = {
    'Ăn uống': 'bg-orange-100 text-orange-700',
    'Mua sắm': 'bg-pink-100 text-pink-700',
    'Di chuyển': 'bg-yellow-100 text-yellow-700',
    'Nhà cửa': 'bg-blue-100 text-blue-700',
    'Giải trí': 'bg-purple-100 text-purple-700',
    'Y tế': 'bg-red-100 text-red-700',
    'Giáo dục': 'bg-indigo-100 text-indigo-700',
    'Hoá đơn & Tiện ích': 'bg-teal-100 text-teal-700',
    'Bảo hiểm': 'bg-cyan-100 text-cyan-700',
    'Du lịch': 'bg-emerald-100 text-emerald-700',
    'Quà tặng & Từ thiện': 'bg-rose-100 text-rose-700',
    'Lương bổng': 'bg-emerald-100 text-emerald-700',
    'Đầu tư': 'bg-sky-100 text-sky-700',
    'Kinh doanh': 'bg-violet-100 text-violet-700',
    'Lãi tiết kiệm': 'bg-lime-100 text-lime-700',
    'Quà tặng': 'bg-rose-100 text-rose-700',
    'Thu nhập thụ động': 'bg-fuchsia-100 text-fuchsia-700',
    'Khác': 'bg-slate-100 text-slate-700'
  };
  return map[category] || 'bg-slate-100 text-slate-700';
}
