/**
 * Button Component JavaScript
 * Provides interactive functionality including:
 * - Ripple animation on click
 * - Debounce protection
 * - State management
 * - Keyboard accessibility
 */

class Button {
  constructor(element, options = {}) {
    this.element = element;
    this.options = {
      debounceTime: 300,
      ripple: true,
      stateDuration: 2000,
      ...options
    };
    
    this.isDebouncing = false;
    this.originalContent = null;
    
    this.init();
  }
  
  init() {
    // Add click event listener
    this.element.addEventListener('click', this.handleClick.bind(this));
    
    // Add keyboard support
    this.element.addEventListener('keydown', this.handleKeydown.bind(this));
    
    // Prevent default if button is loading or disabled
    this.element.addEventListener('click', (e) => {
      if (this.element.classList.contains('btn--loading') || 
          this.element.disabled) {
        e.preventDefault();
        e.stopPropagation();
      }
    }, true);
  }
  
  handleClick(e) {
    // Don't process if disabled or loading
    if (this.element.disabled || 
        this.element.classList.contains('btn--loading') ||
        this.element.classList.contains('btn--disabled')) {
      return;
    }
    
    // Debounce protection
    if (this.isDebouncing) {
      e.preventDefault();
      e.stopPropagation();
      return;
    }
    
    // Create ripple effect
    if (this.options.ripple) {
      this.createRipple(e);
    }
    
    // Start debounce timer
    this.startDebounce();
  }
  
  handleKeydown(e) {
    // Activate on Enter or Space
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      this.element.click();
    }
  }
  
  createRipple(e) {
    const button = this.element;
    const ripple = document.createElement('span');
    ripple.className = 'btn__ripple';
    
    // Calculate position
    const rect = button.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = e.clientX - rect.left - size / 2;
    const y = e.clientY - rect.top - size / 2;
    
    ripple.style.width = ripple.style.height = size + 'px';
    ripple.style.left = x + 'px';
    ripple.style.top = y + 'px';
    
    button.appendChild(ripple);
    
    // Remove ripple after animation
    setTimeout(() => {
      ripple.remove();
    }, 600);
  }
  
  startDebounce() {
    this.isDebouncing = true;
    setTimeout(() => {
      this.isDebouncing = false;
    }, this.options.debounceTime);
  }
  
  // Public methods for state management
  setLoading(loading = true) {
    if (loading) {
      this.originalContent = this.element.innerHTML;
      this.element.classList.add('btn--loading');
      this.element.disabled = true;
      this.element.setAttribute('aria-busy', 'true');
    } else {
      this.element.classList.remove('btn--loading');
      this.element.disabled = false;
      this.element.removeAttribute('aria-busy');
      if (this.originalContent) {
        this.element.innerHTML = this.originalContent;
      }
    }
  }
  
  setDisabled(disabled = true) {
    this.element.disabled = disabled;
    if (disabled) {
      this.element.classList.add('btn--disabled');
      this.element.setAttribute('aria-disabled', 'true');
    } else {
      this.element.classList.remove('btn--disabled');
      this.element.removeAttribute('aria-disabled');
    }
  }
  
  showSuccess(message = '') {
    this.element.classList.add('btn--state-success');
    if (message) {
      const originalText = this.element.textContent;
      this.element.textContent = message;
      setTimeout(() => {
        this.element.textContent = originalText;
        this.element.classList.remove('btn--state-success');
      }, this.options.stateDuration);
    } else {
      setTimeout(() => {
        this.element.classList.remove('btn--state-success');
      }, this.options.stateDuration);
    }
  }
  
  showError(message = '') {
    this.element.classList.add('btn--state-error');
    if (message) {
      const originalText = this.element.textContent;
      this.element.textContent = message;
      setTimeout(() => {
        this.element.textContent = originalText;
        this.element.classList.remove('btn--state-error');
      }, this.options.stateDuration);
    } else {
      setTimeout(() => {
        this.element.classList.remove('btn--state-error');
      }, this.options.stateDuration);
    }
  }
  
  destroy() {
    this.element.removeEventListener('click', this.handleClick);
    this.element.removeEventListener('keydown', this.handleKeydown);
  }
}

// Auto-initialize buttons with data-button attribute
document.addEventListener('DOMContentLoaded', () => {
  const buttons = document.querySelectorAll('[data-button], .btn');
  buttons.forEach(button => {
    if (!button._buttonInstance) {
      button._buttonInstance = new Button(button);
    }
  });
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = Button;
}

// Example usage:
/*
<!-- HTML -->
<button class="btn btn--primary" data-button>
  Click Me
</button>

<button class="btn btn--secondary" data-button>
  <span class="btn__icon btn__icon--leading">
    <svg>...</svg>
  </span>
  With Icon
</button>

// JavaScript
const btn = document.querySelector('.btn');
const buttonInstance = new Button(btn);

// Set loading state
buttonInstance.setLoading(true);

// Show success
setTimeout(() => {
  buttonInstance.setLoading(false);
  buttonInstance.showSuccess('Saved!');
}, 2000);

// Show error
buttonInstance.showError('Failed!');

// Disable/enable
buttonInstance.setDisabled(true);
buttonInstance.setDisabled(false);
*/
