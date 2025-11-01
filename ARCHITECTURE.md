# JamSplitter Full-Stack Music Production Platform

## 🎵 Overview

A comprehensive, modern music production web application designed for deployment on Cloudflare infrastructure. Features professional audio processing tools, a beautiful UI with animations and rich colors, and enterprise-grade security and compliance features.

## ✨ What's Included

### 🎨 Frontend Components

#### Design System
- **Comprehensive CSS Design System** (`frontend/styles/design-system.css`)
  - Rich color palette (primary blues, secondary purples, accent cyan)
  - Google Fonts integration (Inter, Poppins)
  - Soft rounded edges (4px to 32px radius scale)
  - Professional shadows with colored variants
  - Smooth animations and transitions
  - Full dark mode support
  - Responsive typography scale
  - Custom scrollbar styling

#### Button Component
- **Location**: `frontend/components/Button/`
- **Features**:
  - 6 variants (primary, secondary, tertiary, danger, success, ghost)
  - 5 sizes (xs, sm, md, lg, xl)
  - Loading states with animated spinner
  - Ripple click animation effect
  - Debounce protection (300ms default)
  - Icon support (leading/trailing)
  - Success/error state transitions
  - Full keyboard accessibility
  - Button groups (horizontal/vertical)
  - Disabled and loading states
- **Files**: `Button.css`, `Button.js`

#### Message Pane Component
- **Location**: `frontend/components/MessagePane/`
- **Features**:
  - Toast notifications (success, error, warning, info)
  - Slide-in animations from right
  - Auto-dismiss with configurable timeout
  - Manual dismiss capability
  - Message queue system (max 5 concurrent)
  - Progress bars for processing updates
  - Action buttons (undo, retry, custom actions)
  - Notification center with history
  - Screen reader accessible (ARIA roles)
  - Sound effects support (optional)
- **Files**: `MessagePane.css`, `MessagePane.js`

#### Card Component
- **Location**: `frontend/components/Card/`
- **Features**:
  - Multiple variants (project, track, effect, compact)
  - Hover elevation animations
  - Thumbnail with overlay actions
  - Badge support
  - Header, body, footer sections
  - Metadata display
  - Progress bars
  - Skeleton loading states
  - Drag-and-drop support
  - Selection states
  - Grid and list layouts
- **File**: `Card.css`

### 🎛️ Audio Processing (Backend)

#### Reverb Effect Processor
- **Location**: `backend/audio/effects/reverb.py`
- **Algorithm**: Schroeder reverberator with comb and allpass filters
- **Parameters**:
  - Room size (0.0 - 1.0)
  - Damping/decay (0.0 - 1.0)
  - Wet/dry mix (0.0 - 1.0)
  - Stereo width (0.0 - 1.0)
  - Early reflections (0.0 - 1.0)
  - Pre-delay (0-100ms)
- **Presets**: small_room, medium_room, large_hall, chamber, plate, cathedral
- **Features**:
  - High-quality convolution reverb
  - Adjustable stereo width
  - Early reflections simulation
  - Damping for natural decay

#### Parametric Equalizer
- **Location**: `backend/audio/effects/equalizer.py`
- **Algorithm**: Biquad filters (IIR)
- **Band Types**:
  - Bell (parametric)
  - Low shelf
  - High shelf
  - Low pass
  - High pass
  - Notch
- **Parameters per band**:
  - Frequency (20Hz - 20kHz)
  - Gain (-20dB to +20dB)
  - Q factor (0.1 - 10)
- **Presets**: flat, vocal_clarity, bass_boost, bright, warm, radio, mastering
- **Features**:
  - 5-10 customizable bands
  - Frequency response calculation
  - Enable/disable individual bands
  - Professional biquad implementation

### 🗄️ Database Schema

**Location**: `cloudflare/schema/0001_initial_schema.sql`

**Tables** (15+ comprehensive tables):
- `users` - User accounts with OAuth support
- `projects` - Music projects
- `tracks` - Individual audio files
- `processing_jobs` - Async job tracking
- `audio_stems` - Separated audio components
- `effect_presets` - Saved effect configurations
- `effect_chains` - Ordered effects on tracks
- `lyrics` - Synchronized lyrics with timestamps
- `usage_logs` - Analytics and rate limiting
- `audit_logs` - Security and compliance
- `api_keys` - API key management
- `quotas` - User usage limits
- `project_shares` - Collaboration
- `content_reports` - Moderation
- And more...

### ☁️ Cloudflare Infrastructure

**Configuration**: `wrangler.toml`

- **Cloudflare Workers** - Serverless API
- **Cloudflare Pages** - Static site hosting
- **Cloudflare D1** - SQL database
- **Cloudflare R2** - Object storage (audio files)
- **Cloudflare KV** - Caching and sessions
- **Cloudflare Queues** - Async job processing
- **Cloudflare AI** - AI-powered features
- **Durable Objects** - Real-time sessions

## 📋 Task List

**Location**: `tasks.md`

Comprehensive task breakdown with 10 phases:
1. Architecture & Foundation (Days 1-3)
2. Frontend UI/UX System (Days 4-8)
3. Audio Processing Backend (Days 9-16)
4. Advanced Features (Days 17-21)
5. Security & Compliance (Days 22-24)
6. Cloudflare Deployment (Days 25-27)
7. Testing & Quality Assurance (Days 28-30)
8. Documentation & Polish (Days 31-33)
9. Launch Preparation (Days 34-35)
10. Post-Launch (Ongoing)

**Total**: 200+ microgoals with completion criteria

## 🚀 Getting Started

### Prerequisites

- Node.js 18+
- Python 3.11+
- Cloudflare account
- Wrangler CLI (`npm install -g wrangler`)

### Installation

```bash
# Clone repository
git clone https://github.com/cbwinslow/JamSplitter.git
cd JamSplitter

# Install Python dependencies
pip install -r requirements.txt

# Install Node dependencies (for Cloudflare Workers)
npm install

# Login to Cloudflare
wrangler login
```

### Development

```bash
# Start Cloudflare Workers development server
wrangler dev

# Run Python backend locally
python app.py

# Watch frontend changes
npm run dev
```

### Deployment

```bash
# Deploy to Cloudflare
wrangler deploy

# Run database migrations
wrangler d1 execute jamsplitter-db --file=cloudflare/schema/0001_initial_schema.sql
```

## 🎨 Design System Usage

### Colors

```css
/* Primary colors */
var(--color-primary-500)  /* Main brand color */
var(--color-primary-600)  /* Hover state */

/* Semantic colors */
var(--color-success-500)
var(--color-error-500)
var(--color-warning-500)

/* Neutrals */
var(--color-gray-50) to var(--color-gray-900)
```

### Typography

```css
/* Font families */
var(--font-primary)   /* Inter */
var(--font-heading)   /* Poppins */

/* Sizes */
var(--text-xs) to var(--text-6xl)

/* Weights */
var(--font-light) to var(--font-black)
```

### Spacing

```css
/* Spacing scale (4px base) */
var(--spacing-1)  /* 4px */
var(--spacing-4)  /* 16px */
var(--spacing-8)  /* 32px */
```

### Border Radius

```css
/* Soft edges */
var(--radius-sm)   /* 4px */
var(--radius-lg)   /* 12px */
var(--radius-xl)   /* 16px */
var(--radius-2xl)  /* 24px */
```

## 🧩 Component Usage

### Button Component

```html
<button class="btn btn--primary btn--lg">
  <span class="btn__icon btn__icon--leading">
    <svg>...</svg>
  </span>
  <span class="btn__text">Click Me</span>
</button>
```

```javascript
// Initialize button
const btn = new Button(document.querySelector('.btn'));

// Show loading
btn.setLoading(true);

// Show success
btn.showSuccess('Saved!');

// Show error
btn.showError('Failed!');
```

### Message Pane

```javascript
// Success message
messagePane.success('Success!', 'Your file has been uploaded.');

// Error with retry
messagePane.error('Upload Failed', 'Could not upload file.', {
  actions: [
    {
      id: 'retry',
      label: 'Retry',
      variant: 'primary',
      onClick: () => console.log('Retrying...')
    }
  ]
});

// Progress message
const msg = messagePane.info('Processing', 'Please wait...', {
  progress: 0,
  duration: 0
});

// Update progress
messagePane.updateProgress(msg, 50);
```

### Card Component

```html
<div class="card card--project">
  <div class="card__thumbnail">
    <img src="project.jpg" alt="Project">
    <div class="card__badge card__badge--primary">New</div>
  </div>
  <div class="card__body">
    <h3 class="card__title">My Project</h3>
    <p class="card__description">A cool music project</p>
  </div>
  <div class="card__footer">
    <button class="btn btn--primary btn--sm">Open</button>
  </div>
</div>
```

## 🎛️ Audio Processing Usage

### Reverb

```python
from backend.audio.effects.reverb import ReverbProcessor

# Create processor
reverb = ReverbProcessor(sample_rate=44100)

# Use preset
reverb.set_preset('large_hall')

# Or customize
reverb.set_parameters(
    room_size=0.7,
    damping=0.4,
    wet_dry_mix=0.35
)

# Process audio
audio_output = reverb.process(audio_input)
```

### Equalizer

```python
from backend.audio.effects.equalizer import ParametricEqualizer

# Create EQ
eq = ParametricEqualizer(sample_rate=44100)

# Load preset
eq.load_preset('vocal_clarity')

# Customize band
eq.set_band(0, frequency=80, gain=3, q=0.7)

# Process audio
audio_output = eq.process(audio_input)

# Get frequency response
response = eq.get_frequency_response()
```

## 🔐 Security Features

- **Authentication**: JWT-based with OAuth2 support
- **Authorization**: Role-based access control (free, pro, admin)
- **Rate Limiting**: IP and user-based limits
- **Anti-Piracy**: Audio watermarking and fingerprinting
- **Content Validation**: File type and malware scanning
- **Compliance**: GDPR, audit logs, data retention policies
- **API Keys**: Secure key management with rate limits

## 📊 Monitoring

- **Usage Logs**: Track all user actions
- **Audit Logs**: Security event tracking
- **Error Tracking**: Sentry integration ready
- **Performance Metrics**: Prometheus-compatible
- **Uptime Monitoring**: Health check endpoints

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=backend tests/

# Frontend tests
npm test
```

## 📖 Documentation

- **API Documentation**: Auto-generated OpenAPI/Swagger docs
- **Component Documentation**: Inline CSS/JS comments
- **Database Schema**: Comprehensive SQL with comments
- **Task Breakdown**: `tasks.md` with microgoals

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Design inspired by modern music production tools
- Audio algorithms based on industry-standard DSP techniques
- Built with Cloudflare's edge computing platform

## 📬 Contact

- **Project**: [GitHub Repository](https://github.com/cbwinslow/JamSplitter)
- **Issues**: [GitHub Issues](https://github.com/cbwinslow/JamSplitter/issues)

## 🗺️ Roadmap

See `tasks.md` for the complete roadmap with:
- 10 development phases
- 200+ microgoals
- Completion criteria for each task
- Risk mitigation strategies
- Success metrics

---

**Built with ❤️ for music producers and audio engineers**
