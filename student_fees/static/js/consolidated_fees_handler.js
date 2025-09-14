// Consolidated Fees Handler - Merged functionality from all JS files
// Cache bust: v1.1
class ConsolidatedFeeManager {
    constructor() {
        this.apiEndpoints = {
            getStudentFees: '/student_fees/api/student-fees/',
            processPayment: '/student_fees/api/process-payment/'
        };
        this.currentForm = null;
        this.init();
    }

    init() {
        this.setupCSRF();
        this.bindEvents();
    }

    setupCSRF() {
        this.csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
                        document.querySelector('meta[name=csrf-token]')?.getAttribute('content') || 
                        '';
    }

    bindEvents() {
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('view-fees-btn') || e.target.closest('.view-fees-btn')) {
                this.handleViewFeesClick(e);
            }
        });

        document.addEventListener('change', (e) => {
            if (e.target.classList.contains('discount-toggle')) {
                this.handleDiscountToggle(e);
            }
        });
    }

    async handleViewFeesClick(e) {
        const button = e.target.classList.contains('view-fees-btn') ? e.target : e.target.closest('.view-fees-btn');
        const studentId = button.getAttribute('data-student-id');
        const admissionNumber = button.getAttribute('data-admission-number');
        
        if (!studentId || !admissionNumber) {
            this.showMessage('Missing student data', 'error');
            return;
        }

        const container = document.getElementById('fees-container-' + admissionNumber);
        if (!container) {
            this.showMessage('Fees container not found', 'error');
            return;
        }

        if (container.classList.contains('hidden')) {
            await this.loadStudentFees(studentId, admissionNumber, button, container);
        } else {
            this.hideFeesContainer(button, container);
        }
    }

    async loadStudentFees(studentId, admissionNumber, button, container) {
        try {
            this.updateButtonState(button, 'loading');
            container.classList.remove('hidden');
            container.innerHTML = this.getLoadingHTML();

            const studentCard = button.closest('.student-card');
            const discountToggle = studentCard.querySelector('.discount-toggle');
            const isDiscountEnabled = discountToggle ? discountToggle.checked : false;

            // Use centralized service endpoint with auto-sync
            const response = await fetch(`${this.apiEndpoints.getStudentFees}?admission_number=${encodeURIComponent(admissionNumber)}&isDiscountEnabled=${isDiscountEnabled}&auto_sync=true`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();

            if (data.status === 'success') {
                container.innerHTML = data.html || this.renderFeesForm(data, isDiscountEnabled);
                this.initializeFeesForm(admissionNumber);
                this.updateButtonState(button, 'close');
                
                // Show sync notification if new fees/fines were detected
                if (data.sync_info && data.sync_info.new_items > 0) {
                    this.showMessage(`✨ Found ${data.sync_info.new_items} new fees/fines and applied them automatically!`, 'success');
                }
            } else {
                container.innerHTML = this.getErrorHTML(data.message || 'Error loading fees');
            }

        } catch (error) {
            console.error('Error loading fees:', error);
            container.innerHTML = this.getErrorHTML(`Failed to load fees: ${error.message}`);
        }
    }

    hideFeesContainer(button, container) {
        container.classList.add('hidden');
        this.updateButtonState(button, 'process');
    }

    updateButtonState(button, state) {
        const states = {
            process: {
                text: '<i class="fas fa-money-check-alt mr-2"></i>Process Payment',
                classes: 'from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700'
            },
            loading: {
                text: '<i class="fas fa-spinner fa-spin mr-2"></i>Loading...',
                classes: 'from-blue-500 to-blue-600'
            },
            close: {
                text: '<i class="fas fa-times mr-2"></i>Close Payment',
                classes: 'from-red-500 to-red-600 hover:from-red-600 hover:to-red-700'
            }
        };

        const config = states[state];
        if (config) {
            button.innerHTML = config.text;
            button.className = button.className.replace(/from-\w+-\d+|to-\w+-\d+|hover:from-\w+-\d+|hover:to-\w+-\d+/g, '');
            button.className += ' ' + config.classes;
        }
    }

    renderFeesForm(data, discountEnabled) {
        const { student, payable_fees } = data;
        
        if (!payable_fees || payable_fees.length === 0) {
            return `
                <div class="bg-green-50 border-2 border-green-200 rounded-xl p-8 text-center">
                    <i class="fas fa-check-circle text-green-500 text-4xl mb-4"></i>
                    <h3 class="text-xl font-bold text-green-800 mb-2">All Fees Paid!</h3>
                    <p class="text-green-600">This student has no pending fees.</p>
                </div>
            `;
        }

        return `
            <div class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-200">
                <form id="depositForm-${student.admission_number}" action="${this.apiEndpoints.processPayment}" method="POST" class="space-y-6">
                    <input type="hidden" name="csrfmiddlewaretoken" value="${this.csrfToken}">
                    <input type="hidden" name="student_id" value="${student.id}">
                    
                    <div class="bg-white rounded-xl shadow-lg overflow-hidden">
                        <div class="bg-gradient-to-r from-blue-500 to-indigo-600 p-4">
                            <h3 class="text-white font-bold text-lg flex items-center">
                                <i class="fas fa-list-alt mr-2"></i>Payable Fees
                            </h3>
                        </div>
                        
                        <div class="overflow-x-auto">
                            <table class="w-full">
                                <thead class="bg-gray-50">
                                    <tr>
                                        <th class="px-4 py-3 text-left">Select</th>
                                        <th class="px-4 py-3 text-left">Fee Type</th>
                                        <th class="px-4 py-3 text-right">Amount</th>
                                        ${discountEnabled ? '<th class="px-4 py-3 text-right">Discount</th>' : ''}
                                        <th class="px-4 py-3 text-right">Payable</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${payable_fees.map(fee => this.renderFeeRow(fee, discountEnabled)).join('')}
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <div class="bg-white rounded-xl p-6 shadow-lg">
                        <h4 class="font-bold text-lg mb-4 flex items-center">
                            <i class="fas fa-calculator mr-2 text-blue-500"></i>Payment Summary
                        </h4>
                        <div class="grid grid-cols-3 gap-4 text-center">
                            <div class="bg-blue-50 rounded-lg p-4">
                                <div class="text-sm text-gray-600">Total Selected</div>
                                <div id="total_selected" class="text-xl font-bold text-blue-600">₹ 0.00</div>
                            </div>
                            <div class="bg-green-50 rounded-lg p-4">
                                <div class="text-sm text-gray-600">Total Discount</div>
                                <div id="total_discount" class="text-xl font-bold text-green-600">₹ 0.00</div>
                            </div>
                            <div class="bg-purple-50 rounded-lg p-4">
                                <div class="text-sm text-gray-600">Total Payable</div>
                                <div id="total_payable" class="text-xl font-bold text-purple-600">₹ 0.00</div>
                            </div>
                        </div>
                    </div>

                    ${this.renderPaymentDetailsForm()}

                    <div class="text-center">
                        <button type="submit" class="bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white font-bold py-4 px-8 rounded-xl transition-all duration-300 transform hover:scale-105 shadow-lg">
                            <i class="fas fa-credit-card mr-2"></i>Process Payment
                        </button>
                    </div>
                </form>
            </div>
        `;
    }

    renderFeeRow(fee, discountEnabled) {
        const isOverdue = fee.is_overdue ? 'bg-red-50 border-l-4 border-red-400' : '';
        const overdueIcon = fee.is_overdue ? '<i class="fas fa-exclamation-triangle text-red-500 mr-1"></i>' : '';
        
        return `
            <tr class="fee-row border-b hover:bg-gray-50 ${isOverdue}">
                <td class="px-4 py-3">
                    <input type="checkbox" class="fee-checkbox form-checkbox h-5 w-5 text-blue-600" 
                           name="selected_fees" value="${fee.id}" data-amount="${fee.amount}">
                </td>
                <td class="px-4 py-3">
                    <div class="font-medium">${overdueIcon}${fee.display_name}</div>
                    ${fee.due_date ? `<div class="text-sm text-red-600">Due: ${fee.due_date}</div>` : ''}
                </td>
                <td class="px-4 py-3 text-right">
                    <span class="fee-amount font-semibold">₹ ${fee.amount.toFixed(2)}</span>
                    <input type="hidden" name="amount_${fee.id}" value="${fee.amount}">
                </td>
                ${discountEnabled ? `
                    <td class="px-4 py-3 text-right">
                        <input type="number" class="discount-input w-20 px-2 py-1 border rounded text-right" 
                               name="discount_${fee.id}" min="0" max="${fee.amount}" step="0.01" value="0">
                    </td>
                ` : ''}
                <td class="px-4 py-3 text-right">
                    <span class="payable-amount font-bold text-green-600">₹ ${fee.amount.toFixed(2)}</span>
                </td>
            </tr>
        `;
    }

    renderPaymentDetailsForm() {
        return `
            <div class="bg-white rounded-xl p-6 shadow-lg">
                <h4 class="font-bold text-lg mb-4 flex items-center">
                    <i class="fas fa-credit-card mr-2 text-blue-500"></i>Payment Details
                </h4>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Payment Method *</label>
                        <select id="payment_mode" name="payment_mode" class="w-full px-3 py-2 border border-gray-300 rounded-lg" required>
                            <option value="Cash">Cash</option>
                            <option value="Online">Online Transfer</option>
                            <option value="UPI">UPI</option>
                            <option value="Cheque">Cheque</option>
                            <option value="Card">Card</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Payment Date *</label>
                        <input type="datetime-local" id="deposit_date" name="deposit_date" 
                               class="w-full px-3 py-2 border border-gray-300 rounded-lg" required>
                    </div>
                </div>
                
                <div id="extra_fields" class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4" style="display: none;">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Transaction Number</label>
                        <input type="text" id="trans_no" name="transaction_no" 
                               class="w-full px-3 py-2 border border-gray-300 rounded-lg">
                    </div>
                    <div>
                        <label id="source_label" class="block text-sm font-medium text-gray-700 mb-2">Payment Source</label>
                        <input type="text" id="pay_source" name="payment_source" 
                               class="w-full px-3 py-2 border border-gray-300 rounded-lg">
                    </div>
                </div>
            </div>
        `;
    }

    initializeFeesForm(admissionNumber) {
        const form = document.getElementById('depositForm-' + admissionNumber);
        if (!form) return;

        // Set current date and time
        const now = new Date();
        const dateInput = form.querySelector('#deposit_date');
        if (dateInput) {
            dateInput.value = now.toISOString().slice(0, 16);
        }

        // Payment method change handler
        const paymentModeSelect = form.querySelector('#payment_mode');
        const extraFields = form.querySelector('#extra_fields');
        
        if (paymentModeSelect && extraFields) {
            paymentModeSelect.addEventListener('change', () => {
                this.togglePaymentFields(paymentModeSelect.value, extraFields, form);
            });
        }

        // Fee selection and calculation handlers
        form.querySelectorAll('.fee-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', () => this.updateTotals(form));
        });

        form.querySelectorAll('.discount-input').forEach(input => {
            input.addEventListener('input', () => this.updateTotals(form));
        });

        // Form submission
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleFormSubmission(form);
        });

        // Initialize totals
        this.updateTotals(form);
    }

    togglePaymentFields(mode, extraFields, form) {
        const sourceLabel = form.querySelector('#source_label');
        const transInput = form.querySelector('#trans_no');
        const sourceInput = form.querySelector('#pay_source');

        if (mode === 'Cash') {
            extraFields.style.display = 'none';
        } else {
            extraFields.style.display = 'grid';
            
            const configs = {
                'Cheque': { label: 'Bank Name', transPlaceholder: 'Cheque Number', sourcePlaceholder: 'Enter bank name' },
                'UPI': { label: 'UPI App', transPlaceholder: 'UPI Reference', sourcePlaceholder: 'Enter UPI app' },
                'Online': { label: 'Bank/Platform', transPlaceholder: 'Transaction ID', sourcePlaceholder: 'Enter platform' },
                'Card': { label: 'Card Issuer', transPlaceholder: 'Last 4 digits', sourcePlaceholder: 'Enter issuer' }
            };

            const config = configs[mode] || configs['Online'];
            if (sourceLabel) sourceLabel.textContent = config.label;
            if (transInput) transInput.placeholder = config.transPlaceholder;
            if (sourceInput) sourceInput.placeholder = config.sourcePlaceholder;
        }
    }

    updateTotals(form) {
        let selectedTotal = 0;
        let totalDiscount = 0;

        form.querySelectorAll('.fee-row').forEach(row => {
            const checkbox = row.querySelector('.fee-checkbox');
            const amountText = row.querySelector('.fee-amount').textContent;
            const amount = parseFloat(amountText.replace('₹', '').replace(',', '').trim()) || 0;
            
            if (checkbox && checkbox.checked) {
                const discountInput = row.querySelector('.discount-input');
                let discount = 0;
                
                if (discountInput) {
                    discount = parseFloat(discountInput.value) || 0;
                    if (discount > amount) {
                        discount = amount;
                        discountInput.value = discount.toFixed(2);
                    }
                }

                const payableAmount = amount - discount;
                const payableCell = row.querySelector('.payable-amount');
                if (payableCell) {
                    payableCell.textContent = `₹ ${payableAmount.toFixed(2)}`;
                }

                selectedTotal += amount;
                totalDiscount += discount;
                row.classList.add('bg-green-50');
            } else {
                const payableCell = row.querySelector('.payable-amount');
                const amountCell = row.querySelector('.fee-amount');
                if (payableCell && amountCell) {
                    payableCell.textContent = amountCell.textContent;
                }
                row.classList.remove('bg-green-50');
            }
        });

        const payable = selectedTotal - totalDiscount;
        
        // Update summary
        const totalSelectedEl = form.querySelector('#total_selected');
        const totalDiscountEl = form.querySelector('#total_discount');
        const totalPayableEl = form.querySelector('#total_payable');

        if (totalSelectedEl) totalSelectedEl.textContent = `₹ ${selectedTotal.toFixed(2)}`;
        if (totalDiscountEl) totalDiscountEl.textContent = `₹ ${totalDiscount.toFixed(2)}`;
        if (totalPayableEl) totalPayableEl.textContent = `₹ ${payable.toFixed(2)}`;
    }

    async handleFormSubmission(form) {
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        
        try {
            const selectedFees = form.querySelectorAll('.fee-checkbox:checked');
            if (selectedFees.length === 0) {
                this.showMessage('Please select at least one fee to pay.', 'error');
                return;
            }

            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Processing...';
            submitBtn.disabled = true;

            // Use standard form submission for better compatibility
            const formData = new FormData(form);
            
            // Add CSRF token
            formData.append('csrfmiddlewaretoken', this.csrfToken);
            
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': this.csrfToken
                }
            });

            const result = await response.json();

            if (result.status === 'success') {
                this.showMessage(result.message, 'success');
                
                // Show sync notification if available
                if (result.sync_info && result.sync_info.post_payment_updates > 0) {
                    this.showMessage(`🔄 Updated ${result.sync_info.post_payment_updates} related records automatically!`, 'info');
                }
                
                // Redirect to confirmation page
                setTimeout(() => {
                    document.body.style.opacity = '0.8';
                    document.body.style.transition = 'opacity 0.3s ease';
                    window.location.href = result.redirect_url || `/student_fees/payment-confirmation/${formData.get('student_id')}/?receipt_no=${result.receipt_no}`;
                }, 800);
            } else {
                this.showMessage(result.message || 'Payment failed', 'error');
            }

        } catch (error) {
            console.error('Payment submission error:', error);
            this.showMessage('Network error: ' + error.message, 'error');
        } finally {
            if (submitBtn) {
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            }
        }
    }

    handleDiscountToggle(e) {
        const studentCard = e.target.closest('.student-card');
        const admissionNumber = studentCard.querySelector('.view-fees-btn').getAttribute('data-admission-number');
        
        const container = document.getElementById('fees-container-' + admissionNumber);
        if (container && !container.classList.contains('hidden')) {
            const button = studentCard.querySelector('.view-fees-btn');
            const studentId = studentCard.getAttribute('data-student-id');
            this.loadStudentFees(studentId, admissionNumber, button, container);
        }
    }

    getLoadingHTML() {
        return `
            <div class="border-2 border-dashed border-blue-300 rounded-xl p-8 text-center">
                <div class="flex justify-center mb-4">
                    <div class="animate-spin rounded-full h-12 w-12 border-4 border-blue-500 border-t-transparent"></div>
                </div>
                <p class="text-lg font-semibold text-gray-700">Loading fees data...</p>
            </div>
        `;
    }

    getErrorHTML(message) {
        return `
            <div class="bg-red-50 border-2 border-red-200 rounded-xl p-6 text-center">
                <i class="fas fa-exclamation-triangle text-red-500 text-3xl mb-3"></i>
                <p class="text-red-700 font-semibold">${message}</p>
            </div>
        `;
    }

    showMessage(message, type = 'info') {
        document.querySelectorAll('.alert-message').forEach(el => el.remove());

        const messageDiv = document.createElement('div');
        messageDiv.className = `alert-message fixed top-4 right-4 z-50 p-4 rounded-xl shadow-lg animate-slide-in`;

        const colors = {
            success: 'bg-green-500 text-white',
            error: 'bg-red-500 text-white',
            info: 'bg-blue-500 text-white'
        };

        messageDiv.className += ' ' + (colors[type] || colors.info);

        const icons = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            info: 'fa-info-circle'
        };

        messageDiv.innerHTML = `
            <div class="flex items-center">
                <i class="fas ${icons[type] || icons.info} mr-3"></i>
                <span class="font-medium">${message}</span>
            </div>
        `;

        document.body.appendChild(messageDiv);

        setTimeout(() => {
            messageDiv.remove();
        }, 5000);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.consolidatedFeeManager = new ConsolidatedFeeManager();
});

// Global function for template onclick handler
function loadStudentFees(button) {
    if (window.consolidatedFeeManager) {
        const studentId = button.getAttribute('data-student-id');
        const admissionNumber = button.getAttribute('data-admission-number');
        const container = document.getElementById('fees-container-' + admissionNumber);
        
        if (container && container.classList.contains('hidden')) {
            window.consolidatedFeeManager.loadStudentFees(studentId, admissionNumber, button, container);
        } else if (container) {
            window.consolidatedFeeManager.hideFeesContainer(button, container);
        }
    }
}