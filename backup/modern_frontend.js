// Modern Frontend Integration - 2025 Standards
class ModernBackupManager {
    constructor() {
        this.apiBase = '/backup/api/v2';
        this.csrfToken = this.getCSRFToken();
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadBackupHistory();
    }

    getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
                     document.querySelector('meta[name=csrf-token]')?.content ||
                     this.getCookie('csrftoken');
        return token;
    }

    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    async apiCall(endpoint, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.csrfToken,
            },
            credentials: 'same-origin'
        };

        const response = await fetch(`${this.apiBase}${endpoint}`, {
            ...defaultOptions,
            ...options,
            headers: { ...defaultOptions.headers, ...options.headers }
        });

        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || `HTTP ${response.status}`);
        }

        return data;
    }

    bindEvents() {
        // Create backup button
        document.getElementById('createBackupBtn')?.addEventListener('click', () => {
            this.showCreateBackupModal();
        });

        // Restore upload
        document.getElementById('restoreUploadBtn')?.addEventListener('click', () => {
            this.showRestoreUploadModal();
        });

        // File input change
        document.getElementById('backupFileInput')?.addEventListener('change', (e) => {
            this.handleFileSelect(e);
        });
    }

    showCreateBackupModal() {
        const modal = document.getElementById('createBackupModal');
        if (modal) {
            modal.style.display = 'block';
            modal.classList.add('show');
        }
    }

    showRestoreUploadModal() {
        const modal = document.getElementById('restoreUploadModal');
        if (modal) {
            modal.style.display = 'block';
            modal.classList.add('show');
        }
    }

    hideModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'none';
            modal.classList.remove('show');
        }
    }

    async createBackup() {
        try {
            this.showProgress('Creating backup...');
            
            const backupType = document.getElementById('backupType')?.value || 'full';
            const backupName = document.getElementById('backupName')?.value || '';

            const response = await this.apiCall('/backups/', {
                method: 'POST',
                body: JSON.stringify({
                    backup_type: backupType,
                    backup_name: backupName
                })
            });

            this.showSuccess(response.message);
            this.hideModal('createBackupModal');
            this.loadBackupHistory();
            
            // Monitor job progress
            if (response.data?.job_id) {
                this.monitorJob(response.data.job_id, 'backup');
            }

        } catch (error) {
            this.showError(`Backup creation failed: ${error.message}`);
        } finally {
            this.hideProgress();
        }
    }

    async restoreFromUpload() {
        try {
            const fileInput = document.getElementById('backupFileInput');
            const restoreMode = document.getElementById('restoreMode')?.value || 'merge';

            if (!fileInput?.files?.length) {
                throw new Error('Please select a backup file');
            }

            this.showProgress('Uploading and restoring backup...');

            const formData = new FormData();
            formData.append('backup_file', fileInput.files[0]);
            formData.append('restore_mode', restoreMode);

            const response = await this.apiCall('/restore/upload/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.csrfToken,
                },
                body: formData
            });

            this.showSuccess(response.message);
            this.hideModal('restoreUploadModal');
            
            // Monitor job progress
            if (response.data?.job_id) {
                this.monitorJob(response.data.job_id, 'restore');
            }

        } catch (error) {
            this.showError(`Restore failed: ${error.message}`);
        } finally {
            this.hideProgress();
        }
    }

    async restoreFromHistory(backupId) {
        try {
            const restoreMode = prompt('Restore mode (merge/replace):', 'merge');
            if (!restoreMode || !['merge', 'replace'].includes(restoreMode)) {
                return;
            }

            if (restoreMode === 'replace') {
                const confirmed = confirm(
                    'WARNING: Replace mode will delete existing data. Are you sure?'
                );
                if (!confirmed) return;
            }

            this.showProgress('Restoring from backup...');

            const response = await this.apiCall(`/restore/history/${backupId}/`, {
                method: 'POST',
                body: JSON.stringify({
                    restore_mode: restoreMode
                })
            });

            this.showSuccess(response.message);
            
            // Monitor job progress
            if (response.data?.job_id) {
                this.monitorJob(response.data.job_id, 'restore');
            }

        } catch (error) {
            this.showError(`Restore failed: ${error.message}`);
        } finally {
            this.hideProgress();
        }
    }

    async loadBackupHistory() {
        try {
            const response = await this.apiCall('/backups/history/');
            this.renderBackupHistory(response.data.backups);
        } catch (error) {
            console.error('Failed to load backup history:', error);
            this.showError('Failed to load backup history');
        }
    }

    renderBackupHistory(backups) {
        const container = document.getElementById('backupHistoryContainer');
        if (!container) return;

        if (!backups?.length) {
            container.innerHTML = '<p class="text-gray-500">No backups found</p>';
            return;
        }

        const html = backups.map(backup => `
            <div class="backup-item bg-white rounded-lg shadow p-4 mb-3">
                <div class="flex justify-between items-center">
                    <div>
                        <h4 class="font-semibold text-gray-800">${this.escapeHtml(backup.file_name)}</h4>
                        <p class="text-sm text-gray-600">
                            ${new Date(backup.date).toLocaleString()} - ${backup.operation_type}
                        </p>
                    </div>
                    <div class="flex space-x-2">
                        <button onclick="backupManager.restoreFromHistory(${backup.id})"
                                class="bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded text-sm">
                            Restore
                        </button>
                        <button onclick="backupManager.downloadBackup(${backup.id})"
                                class="bg-green-500 hover:bg-green-600 text-white px-3 py-1 rounded text-sm">
                            Download
                        </button>
                    </div>
                </div>
            </div>
        `).join('');

        container.innerHTML = html;
    }

    async monitorJob(jobId, jobType) {
        const maxAttempts = 30;
        let attempts = 0;

        const checkStatus = async () => {
            try {
                const response = await this.apiCall(`/${jobType}s/jobs/${jobId}/`);
                const job = response.data;

                if (job.status === 'success') {
                    this.showSuccess(`${jobType} completed successfully`);
                    if (jobType === 'backup') {
                        this.loadBackupHistory();
                    }
                    return;
                } else if (job.status === 'failed') {
                    this.showError(`${jobType} failed: ${job.error || 'Unknown error'}`);
                    return;
                } else if (job.status === 'running' && attempts < maxAttempts) {
                    attempts++;
                    setTimeout(checkStatus, 2000);
                } else {
                    this.showWarning(`${jobType} is taking longer than expected`);
                }
            } catch (error) {
                console.error('Job monitoring error:', error);
            }
        };

        setTimeout(checkStatus, 1000);
    }

    handleFileSelect(event) {
        const file = event.target.files[0];
        const fileInfo = document.getElementById('fileInfo');
        
        if (file && fileInfo) {
            const sizeInMB = (file.size / (1024 * 1024)).toFixed(2);
            fileInfo.innerHTML = `
                <p><strong>File:</strong> ${this.escapeHtml(file.name)}</p>
                <p><strong>Size:</strong> ${sizeInMB} MB</p>
                <p><strong>Type:</strong> ${file.type || 'Unknown'}</p>
            `;
        }
    }

    showProgress(message) {
        const progressDiv = document.getElementById('progressIndicator') || this.createProgressIndicator();
        progressDiv.innerHTML = `
            <div class="flex items-center space-x-3">
                <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
                <span>${this.escapeHtml(message)}</span>
            </div>
        `;
        progressDiv.style.display = 'block';
    }

    hideProgress() {
        const progressDiv = document.getElementById('progressIndicator');
        if (progressDiv) {
            progressDiv.style.display = 'none';
        }
    }

    createProgressIndicator() {
        const div = document.createElement('div');
        div.id = 'progressIndicator';
        div.className = 'fixed top-4 right-4 bg-blue-100 border border-blue-300 rounded-lg p-4 z-50';
        document.body.appendChild(div);
        return div;
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showWarning(message) {
        this.showNotification(message, 'warning');
    }

    showNotification(message, type = 'info') {
        const colors = {
            success: 'bg-green-100 border-green-300 text-green-800',
            error: 'bg-red-100 border-red-300 text-red-800',
            warning: 'bg-yellow-100 border-yellow-300 text-yellow-800',
            info: 'bg-blue-100 border-blue-300 text-blue-800'
        };

        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 ${colors[type]} border rounded-lg p-4 z-50 max-w-md`;
        notification.innerHTML = `
            <div class="flex justify-between items-start">
                <span>${this.escapeHtml(message)}</span>
                <button onclick="this.parentElement.parentElement.remove()" 
                        class="ml-4 text-lg font-bold">&times;</button>
            </div>
        `;

        document.body.appendChild(notification);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.backupManager = new ModernBackupManager();
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ModernBackupManager;
}