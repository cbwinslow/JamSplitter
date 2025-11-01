/**
 * Message Pane Component JavaScript
 * Manages toast notifications and message queue
 */

class MessagePane {
  constructor(options = {}) {
    this.options = {
      position: 'top-right',
      defaultDuration: 5000,
      maxMessages: 5,
      soundEnabled: false,
      queueMessages: true,
      ...options
    };
    
    this.messages = [];
    this.messageQueue = [];
    this.historyMessages = [];
    this.container = null;
    this.notificationCenter = null;
    
    this.init();
  }
  
  init() {
    // Create container
    this.container = document.createElement('div');
    this.container.className = 'message-pane';
    this.container.setAttribute('aria-live', 'polite');
    this.container.setAttribute('aria-atomic', 'false');
    document.body.appendChild(this.container);
    
    // Create notification center
    this.createNotificationCenter();
  }
  
  createNotificationCenter() {
    const center = document.createElement('div');
    center.className = 'notification-center';
    center.innerHTML = `
      <div class="notification-center__header">
        <h2 class="notification-center__title">Notifications</h2>
        <button class="notification-center__close" aria-label="Close notifications">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 6L6 18M6 6l12 12"/>
          </svg>
        </button>
      </div>
      <div class="notification-center__list"></div>
      <div class="notification-center__actions">
        <button class="btn btn--secondary btn--full-width" data-action="clear-all">
          Clear All
        </button>
      </div>
    `;
    
    center.querySelector('.notification-center__close').addEventListener('click', () => {
      this.closeNotificationCenter();
    });
    
    center.querySelector('[data-action="clear-all"]').addEventListener('click', () => {
      this.clearHistory();
    });
    
    document.body.appendChild(center);
    this.notificationCenter = center;
  }
  
  show(type, title, text, options = {}) {
    const messageOptions = {
      type,
      title,
      text,
      duration: options.duration !== undefined ? options.duration : this.options.defaultDuration,
      actions: options.actions || [],
      progress: options.progress,
      dismissible: options.dismissible !== false,
      ...options
    };
    
    if (this.messages.length >= this.options.maxMessages && this.options.queueMessages) {
      this.messageQueue.push(messageOptions);
      return null;
    }
    
    const message = this.createMessage(messageOptions);
    this.messages.push(message);
    this.container.appendChild(message.element);
    
    // Add to history
    this.addToHistory(messageOptions);
    
    // Auto-dismiss
    if (messageOptions.duration > 0) {
      message.timer = setTimeout(() => {
        this.dismiss(message);
      }, messageOptions.duration);
    }
    
    // Play sound
    if (this.options.soundEnabled) {
      this.playSound(type);
    }
    
    return message;
  }
  
  createMessage(options) {
    const element = document.createElement('div');
    element.className = `message message--${options.type}`;
    element.setAttribute('role', options.type === 'error' ? 'alert' : 'status');
    
    const iconSVG = this.getIconSVG(options.type);
    
    let actionsHTML = '';
    if (options.actions && options.actions.length > 0) {
      actionsHTML = '<div class="message__actions">';
      options.actions.forEach(action => {
        const variant = action.variant || 'secondary';
        actionsHTML += `<button class="message__action message__action--${variant}" data-action="${action.id}">${action.label}</button>`;
      });
      actionsHTML += '</div>';
    }
    
    let progressHTML = '';
    if (options.progress !== undefined) {
      const isProcessing = options.progress < 100;
      progressHTML = `
        <div class="message__progress">
          <div class="message__progress-bar ${isProcessing ? 'message__progress-bar--processing' : ''}" 
               style="width: ${options.progress}%"
               role="progressbar" 
               aria-valuenow="${options.progress}" 
               aria-valuemin="0" 
               aria-valuemax="100">
          </div>
        </div>
      `;
    }
    
    const closeButton = options.dismissible ? `
      <button class="message__close" aria-label="Close message">
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M15 5L5 15M5 5l10 10"/>
        </svg>
      </button>
    ` : '';
    
    element.innerHTML = `
      <div class="message__icon">${iconSVG}</div>
      <div class="message__content">
        ${options.title ? `<div class="message__title">${options.title}</div>` : ''}
        ${options.text ? `<div class="message__text">${options.text}</div>` : ''}
        ${actionsHTML}
      </div>
      ${closeButton}
      ${progressHTML}
    `;
    
    // Add close button handler
    if (options.dismissible) {
      element.querySelector('.message__close').addEventListener('click', () => {
        this.dismiss(message);
      });
    }
    
    // Add action handlers
    if (options.actions) {
      options.actions.forEach(action => {
        const button = element.querySelector(`[data-action="${action.id}"]`);
        if (button) {
          button.addEventListener('click', () => {
            if (action.onClick) {
              action.onClick();
            }
            if (action.dismissAfterClick !== false) {
              this.dismiss(message);
            }
          });
        }
      });
    }
    
    const message = {
      element,
      options,
      timer: null,
      id: Date.now() + Math.random()
    };
    
    return message;
  }
  
  getIconSVG(type) {
    const icons = {
      success: `<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
      </svg>`,
      error: `<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
      </svg>`,
      warning: `<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
        <path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/>
      </svg>`,
      info: `<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/>
      </svg>`
    };
    return icons[type] || icons.info;
  }
  
  dismiss(message) {
    if (!message || !message.element) return;
    
    // Clear timer
    if (message.timer) {
      clearTimeout(message.timer);
    }
    
    // Add dismissing class for animation
    message.element.classList.add('message--dismissing');
    
    // Remove after animation
    setTimeout(() => {
      if (message.element.parentNode) {
        message.element.remove();
      }
      
      // Remove from array
      const index = this.messages.indexOf(message);
      if (index > -1) {
        this.messages.splice(index, 1);
      }
      
      // Show queued message
      this.showNextQueued();
    }, 300);
  }
  
  showNextQueued() {
    if (this.messageQueue.length > 0 && this.messages.length < this.options.maxMessages) {
      const nextMessage = this.messageQueue.shift();
      this.show(nextMessage.type, nextMessage.title, nextMessage.text, nextMessage);
    }
  }
  
  updateProgress(message, progress) {
    if (!message || !message.element) return;
    
    const progressBar = message.element.querySelector('.message__progress-bar');
    if (progressBar) {
      progressBar.style.width = `${progress}%`;
      progressBar.setAttribute('aria-valuenow', progress);
      
      // Remove processing class if complete
      if (progress >= 100) {
        progressBar.classList.remove('message__progress-bar--processing');
      }
    }
  }
  
  // Convenience methods
  success(title, text, options) {
    return this.show('success', title, text, options);
  }
  
  error(title, text, options) {
    return this.show('error', title, text, options);
  }
  
  warning(title, text, options) {
    return this.show('warning', title, text, options);
  }
  
  info(title, text, options) {
    return this.show('info', title, text, options);
  }
  
  // Notification center methods
  openNotificationCenter() {
    this.notificationCenter.classList.add('notification-center--open');
    this.renderHistory();
  }
  
  closeNotificationCenter() {
    this.notificationCenter.classList.remove('notification-center--open');
  }
  
  addToHistory(messageOptions) {
    this.historyMessages.unshift({
      ...messageOptions,
      timestamp: new Date()
    });
    
    // Limit history size
    if (this.historyMessages.length > 50) {
      this.historyMessages = this.historyMessages.slice(0, 50);
    }
  }
  
  renderHistory() {
    const list = this.notificationCenter.querySelector('.notification-center__list');
    
    if (this.historyMessages.length === 0) {
      list.innerHTML = `
        <div class="notification-center__empty">
          <svg class="notification-center__empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
            <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
          </svg>
          <p>No notifications yet</p>
        </div>
      `;
      return;
    }
    
    list.innerHTML = this.historyMessages.map(msg => `
      <div class="message message--${msg.type}" style="animation: none;">
        <div class="message__icon">${this.getIconSVG(msg.type)}</div>
        <div class="message__content">
          ${msg.title ? `<div class="message__title">${msg.title}</div>` : ''}
          ${msg.text ? `<div class="message__text">${msg.text}</div>` : ''}
          <div class="message__text" style="font-size: var(--text-xs); opacity: 0.6;">
            ${this.formatTimestamp(msg.timestamp)}
          </div>
        </div>
      </div>
    `).join('');
  }
  
  formatTimestamp(date) {
    const now = new Date();
    const diff = now - date;
    const minutes = Math.floor(diff / 60000);
    
    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    
    const days = Math.floor(hours / 24);
    return `${days}d ago`;
  }
  
  clearHistory() {
    this.historyMessages = [];
    this.renderHistory();
  }
  
  playSound(type) {
    // Implement sound playback if needed
    // Can use Web Audio API or HTML5 Audio
  }
  
  clearAll() {
    this.messages.forEach(message => {
      this.dismiss(message);
    });
    this.messageQueue = [];
  }
}

// Create global instance
const messagePane = new MessagePane();

// Make it available globally
if (typeof window !== 'undefined') {
  window.messagePane = messagePane;
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = MessagePane;
}

// Example usage:
/*
// Show success message
messagePane.success('Success!', 'Your file has been uploaded.');

// Show error with retry action
messagePane.error('Upload Failed', 'Could not upload file.', {
  actions: [
    {
      id: 'retry',
      label: 'Retry',
      variant: 'primary',
      onClick: () => {
        console.log('Retrying...');
      }
    }
  ]
});

// Show processing with progress
const msg = messagePane.info('Processing', 'Please wait...', {
  progress: 0,
  duration: 0 // Don't auto-dismiss
});

// Update progress
let progress = 0;
const interval = setInterval(() => {
  progress += 10;
  messagePane.updateProgress(msg, progress);
  if (progress >= 100) {
    clearInterval(interval);
    messagePane.dismiss(msg);
    messagePane.success('Complete!', 'Processing finished.');
  }
}, 500);

// Open notification center
messagePane.openNotificationCenter();
*/
