// app.js ─────────────────────────────────────────────────────────────
// Author : ChatGPT for CBW  ✦ 2025
// Summary: Frontend JavaScript for JamSplitter web interface

// Configuration
const API_BASE = '/api';
const STATUS_ENDPOINT = '/status';
const SPLIT_ENDPOINT = '/split';
const QUEUE_ENDPOINT = '/queue';

// Utility Functions
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    const bgColors = {
        success: 'bg-green-500',
        error: 'bg-red-500',
        info: 'bg-blue-500',
        warning: 'bg-yellow-500'
    };
    
    toast.className = `${bgColors[type]} text-white px-6 py-4 rounded-lg shadow-lg transform transition-all duration-300 opacity-0 translate-x-full`;
    toast.innerHTML = `
        <div class="flex items-center">
            <span>${message}</span>
            <button onclick="this.parentElement.parentElement.remove()" class="ml-4 text-white hover:text-gray-200">
                <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
            </button>
        </div>
    `;
    
    container.appendChild(toast);
    
    // Trigger animation
    setTimeout(() => {
        toast.classList.remove('opacity-0', 'translate-x-full');
    }, 10);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        toast.classList.add('opacity-0', 'translate-x-full');
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

// DOM Elements
class Elements {
    static get form() { return document.getElementById('processForm'); }
    static get urlInput() { return document.getElementById('url'); }
    static get formatSelect() { return document.getElementById('format'); }
    static get queue() { return document.getElementById('queue'); }
    static get submitButton() { return document.getElementById('submitBtn'); }
    static get btnText() { return document.getElementById('btnText'); }
    static get btnSpinner() { return document.getElementById('btnSpinner'); }
}

// Queue Item class
class QueueItem {
    constructor(url, format, status = { status: 'queued', progress: 0 }) {
        this.url = url;
        this.format = format;
        this.status = status.status;
        this.progress = status.progress;
        this.element = this.createElement();
        this.progressInterval = null;
    }

    createElement() {
        const item = document.createElement('div');
        item.className = 'border border-gray-200 rounded-lg p-4 transition-all hover:shadow-md';
        item.innerHTML = `
            <div class="flex justify-between items-start mb-3">
                <div class="flex-1 mr-4">
                    <p class="text-sm font-medium text-gray-900 break-all">${this.url}</p>
                    <p class="text-xs text-gray-500 mt-1">Format: ${this.format.toUpperCase()}</p>
                </div>
                <span class="status-badge px-3 py-1 rounded-full text-xs font-medium ${this.getStatusClass()}">
                    ${this.status}
                </span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${this.progress * 100}%"></div>
            </div>
            <div class="flex justify-between items-center mt-2">
                <span class="text-xs text-gray-500 progress-text">${Math.round(this.progress * 100)}%</span>
                <button class="remove-btn text-xs text-red-600 hover:text-red-800" style="display: none;">Remove</button>
            </div>
        `;
        
        // Add remove button functionality
        const removeBtn = item.querySelector('.remove-btn');
        removeBtn.addEventListener('click', () => this.remove());
        
        return item;
    }

    getStatusClass() {
        const classes = {
            'queued': 'bg-gray-200 text-gray-700',
            'processing': 'bg-blue-200 text-blue-700',
            'completed': 'bg-green-200 text-green-700',
            'failed': 'bg-red-200 text-red-700'
        };
        return classes[this.status] || 'bg-gray-200 text-gray-700';
    }

    updateStatus(newStatus, progress = 0) {
        this.status = newStatus;
        this.progress = progress;
        
        const statusBadge = this.element.querySelector('.status-badge');
        statusBadge.textContent = newStatus;
        statusBadge.className = `status-badge px-3 py-1 rounded-full text-xs font-medium ${this.getStatusClass()}`;
        
        const progressFill = this.element.querySelector('.progress-fill');
        progressFill.style.width = `${progress * 100}%`;
        
        const progressText = this.element.querySelector('.progress-text');
        progressText.textContent = `${Math.round(progress * 100)}%`;
        
        // Update progress bar color based on status
        if (newStatus === 'completed') {
            progressFill.style.backgroundColor = '#10B981';
            this.element.querySelector('.remove-btn').style.display = 'block';
        } else if (newStatus === 'failed') {
            progressFill.style.backgroundColor = '#EF4444';
            this.element.querySelector('.remove-btn').style.display = 'block';
        } else if (newStatus === 'processing') {
            progressFill.style.backgroundColor = '#3B82F6';
        }
    }

    startPolling() {
        // Simulate progress for demo purposes
        let simulatedProgress = 0;
        this.progressInterval = setInterval(() => {
            if (simulatedProgress < 0.95) {
                simulatedProgress += 0.05 + Math.random() * 0.1;
                this.updateStatus('processing', Math.min(simulatedProgress, 0.95));
            } else {
                // Simulate completion
                this.updateStatus('completed', 1.0);
                this.stopPolling();
                showToast('Processing completed successfully!', 'success');
            }
        }, 1000);
    }

    stopPolling() {
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
        }
    }

    remove() {
        this.stopPolling();
        this.element.classList.add('opacity-0', 'transform', 'scale-95');
        setTimeout(() => {
            this.element.remove();
            QueueManager.checkEmpty();
        }, 300);
    }
}

// Queue Manager
class QueueManager {
    static queueItems = new Map();

    static async initialize() {
        try {
            const response = await fetch(`${API_BASE}${QUEUE_ENDPOINT}`);
            const items = await response.json();
            
            // Add existing items to queue
            for (const [url, status] of Object.entries(items)) {
                const item = new QueueItem(url, status.format || 'mp3', status);
                this.addToDOM(item);
                this.queueItems.set(url, item);
            }
            
            this.checkEmpty();
        } catch (error) {
            console.error('Error initializing queue:', error);
        }
    }

    static addToDOM(item) {
        // Remove empty state if present
        const emptyState = Elements.queue.querySelector('.text-center');
        if (emptyState) {
            emptyState.remove();
        }
        
        Elements.queue.insertBefore(item.element, Elements.queue.firstChild);
    }

    static checkEmpty() {
        if (Elements.queue.children.length === 0) {
            Elements.queue.innerHTML = `
                <div class="text-center py-12 text-gray-400">
                    <svg class="mx-auto h-12 w-12 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
                    </svg>
                    <p class="text-sm">No items in queue</p>
                    <p class="text-xs mt-1">Submit a URL to get started</p>
                </div>
            `;
        }
    }

    static async addItem(url, format) {
        try {
            // Show loading state
            Elements.submitButton.disabled = true;
            Elements.btnText.textContent = 'Processing...';
            Elements.btnSpinner.classList.remove('hidden');

            // Send request to API
            const response = await fetch(`${API_BASE}${SPLIT_ENDPOINT}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    url: url,
                    format: format
                }),
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to process video');
            }

            const result = await response.json();
            
            // Create queue item
            const item = new QueueItem(url, format);
            this.addToDOM(item);
            this.queueItems.set(url, item);
            item.startPolling();

            // Reset form
            Elements.form.reset();
            showToast('Added to processing queue', 'success');

        } catch (error) {
            console.error('Error processing video:', error);
            showToast('Error: ' + error.message, 'error');
        } finally {
            // Reset button state
            Elements.submitButton.disabled = false;
            Elements.btnText.textContent = 'Start Processing';
            Elements.btnSpinner.classList.add('hidden');
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', async () => {
    // Initialize queue
    await QueueManager.initialize();

    // Form submission handler
    Elements.form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const url = Elements.urlInput.value.trim();
        const format = Elements.formatSelect.value;
        
        if (!url) {
            showToast('Please enter a valid URL', 'warning');
            return;
        }
        
        await QueueManager.addItem(url, format);
    });
});
