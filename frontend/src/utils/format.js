export function formatCurrency(value) {
  if (value === null || value === undefined || isNaN(value)) return '0';
  return value.toLocaleString('vi-VN');
}

export function formatOriginalAmount(value, currency) {
  if (value === null || value === undefined || value === 0) return '';
  const cur = currency || 'VND';
  const formatted = Math.abs(value).toLocaleString('vi-VN');
  return `${formatted} ${cur}`;
}

export function formatDate(dateStr) {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  const day = String(d.getDate()).padStart(2, '0');
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const year = d.getFullYear();
  return `${day}/${month}/${year}`;
}

export function formatNumberWithDots(value) {
  if (value === null || value === undefined || isNaN(value)) return '0';
  return value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
}

export function formatTime(dateStr) {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  const hours = String(d.getHours()).padStart(2, '0');
  const mins = String(d.getMinutes()).padStart(2, '0');
  return `${hours}:${mins}`;
}


