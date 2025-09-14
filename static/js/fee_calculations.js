// D:\School-Management-System\School-Management-System-main\student_fees\static\js\fee_calculations.js

// console.log("fee_calculations.js loaded");

export function updateFeeCalculations(form) {
    const rows = form.querySelectorAll('.fee-row');
    let totalAmount = 0;
    let totalDiscount = 0;
    let totalPayable = 0;
    let selectedCount = 0;

    rows.forEach(row => {
        const checkbox = row.querySelector('.fee-checkbox');
        const amountCell = row.querySelector('.fee-amount');
        const discountInput = row.querySelector('.discount-input');
        const payableCell = row.querySelector('.payable-amount');
        
        if (!checkbox || !amountCell || !payableCell) return;

        const isSelected = checkbox.checked;
        const amount = parseFloat(amountCell.textContent.replace(/[^0-9.]/g, '')) || 0;
        const discount = discountInput ? parseFloat(discountInput.value) || 0 : 0;
        const payable = Math.max(0, amount - discount);

        // Update row display
        payableCell.textContent = `₹ ${payable.toFixed(2)}`;
        payableCell.classList.toggle('text-green-600', isSelected);
        payableCell.classList.toggle('text-gray-400', !isSelected);

        // Update totals if selected
        if (isSelected) {
            totalAmount += amount;
            totalDiscount += discount;
            totalPayable += payable;
            selectedCount++;
        }
    });

    // Update summary
    updateSummaryDisplay(form, {
        amount: totalAmount,
        discount: totalDiscount,
        payable: totalPayable,
        selected: selectedCount
    });

    // Toggle submit button
    toggleSubmitButton(form, selectedCount > 0);

    return {
        amount: totalAmount,
        discount: totalDiscount,
        payable: totalPayable,
        selected: selectedCount
    };
}

// This function update all rows
export function updateAllRowDisplays(form) {
    const rows = form.querySelectorAll('.fee-row');
    rows.forEach(row => {
        const { payable, isSelected } = getRowValues(row);
        updateRowDisplay(row, payable, isSelected);
    });
}

export function calculateFeeTotals(form) {
//   console.log("calculateFeeTotals called for form:", form.id);
  const checkboxes = form.querySelectorAll('.fee-checkbox:checked');
  let amount = 0;
  let discount = 0;

  checkboxes.forEach(cb => {
    const row = cb.closest('.fee-row');
    const { amount: rowAmount, discount: rowDiscount } = getRowValues(row);
    // console.log("Row Values:", rowAmount, rowDiscount);
    amount += rowAmount;
    discount += rowDiscount;
  });

  const payable = amount - discount;
//   console.log("Calculated totals from fee_calculations:", { amount, discount, payable, selected: checkboxes.length });
  return { amount, discount, payable, selected: checkboxes.length };
}

function getRowValues(row) {
    const checkbox = row.querySelector('.fee-checkbox');
    const amountCell = row.querySelector('.fee-amount');
    const discountInput = row.querySelector('.discount-input');
    
    const amount = parseFloat(amountCell?.textContent.replace(/[^0-9.]/g, '') || 0);
    const discount = parseFloat(discountInput?.value || 0);
    const payable = Math.max(0, amount - discount);
    const isSelected = checkbox?.checked || false;
    
    // console.log("getRowValues for row:", { amount, discount, payable, isSelected });
    return { amount, discount, payable, isSelected };
}

function updateRowDisplay(row, payable, isSelected) {
    const payableCell = row.querySelector('.payable-amount');
    if (!payableCell) return;

    payableCell.textContent = `₹ ${payable.toFixed(2)}`;
    payableCell.classList.toggle('text-green-600', isSelected);
    payableCell.classList.toggle('text-gray-400', !isSelected);
    // console.log("updateRowDisplay for row:", row, payable, isSelected);
}

function updateSummaryDisplay(form, { amount, discount, payable }) {
    // console.log("updateSummaryDisplay called with:", { amount, discount, payable });
    const updateElement = (selector, value) => {
        const el = form.querySelector(selector);
        if (el) {
            el.textContent = `₹ ${value.toFixed(2)}`;
            // console.log("Updated element", selector, "to", el.textContent);
        }
    };

    updateElement('#total_selected', amount);
    updateElement('#total_discount', discount);
    updateElement('#total_payable', payable);
}

function toggleSubmitButton(form, enabled) {
    // console.log("toggleSubmitButton called, enabled:", enabled);
    const submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) {
        submitBtn.disabled = !enabled;
        // console.log("Submit button", submitBtn, "disabled:", submitBtn.disabled);
    }
}