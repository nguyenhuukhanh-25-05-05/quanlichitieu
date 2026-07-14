import { ref, watch } from 'vue';
import { formatNumberWithDots } from '../utils/format';

export function useAmountInput(formField, formFieldName) {
  const amountInputStr = ref('');

  const onAmountInput = (e) => {
    let raw = e.target.value.replace(/[^0-9]/g, '');
    if (raw === '') {
      amountInputStr.value = '';
      formField[formFieldName] = null;
      return;
    }
    raw = raw.replace(/^0+/, '');
    const val = parseFloat(raw) || 0;
    formField[formFieldName] = val;
    amountInputStr.value = formatNumberWithDots(val);
  };

  watch(
    () => formField[formFieldName],
    (newVal) => {
      if (newVal === null || newVal === undefined || newVal === '') {
        amountInputStr.value = '';
      } else {
        amountInputStr.value = formatNumberWithDots(newVal);
      }
    }
  );

  return { amountInputStr, onAmountInput };
}
