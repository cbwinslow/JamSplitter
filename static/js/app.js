// app.js ─────────────────────────────────────────────────────────────
// Author : ChatGPT for CBW  ✦ 2025-05-24
// Summary: Frontend JavaScript for JamSplitter web interface

// Configuration
const API_BASE = '/api';
const STATUS_ENDPOINT = '/status';
const SPLIT_ENDPOINT = '/split';
const QUEUE_ENDPOINT = '/queue';

// DOM Elements
class Elements {
    static get form() { return document.getElementById('processForm'); }
    static get urlInput() { return document.getElementById('url'); }
    static get formatSelect() { return document.getElementById('format'); }
    static get queue() { return document.getElementById('queue'); }
    static get submitButton() { return this.form.querySelector('button[type="submit"]'); }
}

// Queue Item class
class QueueItem {
    constructor(url, element) {
        this.url = url;
        this.element = element;
        this.statusSpan = element.querySelector('.text-gray-500');
        this.progressBar = element.querySelector('.progress-fill');
        this.progressInterval = null;
    }

    updateStatus(status, progress = 0) {
        this.statusSpan.textContent = status;
        this.progressBar.style.width = `${progress * 100}%`;
        
        // Update progress bar color based on status
        if (status === 'Completed') {
            this.progressBar.style.backgroundColor = '#10B981';
        } else if (status === 'Failed') {
            this.progressBar.style.backgroundColor = '#EF4444';
        }
    }

    startPolling() {
        this.pollStatus();
        this.progressInterval = setInterval(() => this.pollStatus(), 1000);
    }

    stopPolling() {
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
        }
    }

    async pollStatus() {
        try {
            const response = await fetch(`${API_BASE}${STATUS_ENDPOINT}/${this.url}`);
            const data = await response.json();

            if (data.status === 'processing') {
                this.updateStatus('Processing...', data.progress);
            } else if (data.status === 'completed') {
                this.updateStatus('Completed', 1);
                this.stopPolling();
            } else if (data.status === 'failed') {
                this.updateStatus('Failed', 0);
                this.stopPolling();
            }
        } catch (error) {
            console.error('Error checking status:', error);
            this.updateStatus('Error', 0);
            this.stopPolling();
        }
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
                const item = this.createQueueItem(url, status);
                this.queueItems.set(url, item);
            }
        } catch (error) {
            console.error('Error initializing queue:', error);
        }
    }

    static createQueueItem(url, status = { status: 'processing', progress: 0 }) {
        const item = document.createElement('div');
        item.className = 'bg-gray-50 p-4 rounded-lg';
        item.innerHTML = `
            <div class="flex justify-between items-center mb-2">
                <span class="font-medium">${url}</span>
                <span class="text-sm text-gray-500">${status.status}</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${status.progress * 100}%"></div>
            </div>
        `;
        
        Elements.queue.insertBefore(item, Elements.queue.firstChild);
        return new QueueItem(url, item);
    }

    static async addItem(url, format) {
        try {
            // Disable form
            Elements.submitButton.disabled = true;
            Elements.submitButton.textContent = 'Processing...';

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
                throw new Error('Failed to process video');
            }

            // Create queue item
            const item = this.createQueueItem(url);
            this.queueItems.set(url, item);
            item.startPolling();

        } catch (error) {
            alert('Error processing video: ' + error.message);
            Elements.submitButton.disabled = false;
            Elements.submitButton.textContent = 'Process Video';
        }
    }

    static removeItem(url) {
        const item = this.queueItems.get(url);
        if (item) {
            item.element.remove();
            this.queueItems.delete(url);
        }
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    // Initialize queue
    await QueueManager.initialize();

    // Form submission handler
    Elements.form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const url = Elements.urlInput.value;
        const format = Elements.formatSelect.value;
        await QueueManager.addItem(url, format);
    });
});
