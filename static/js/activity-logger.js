/**
 * Activity Logger - AI Memory System
 *
 * Tracks user interactions and sends them to the backend in batches.
 * Used for pattern detection, engagement analysis, and behavioral insights.
 */

class ActivityLogger {
    constructor() {
        this.currentSessionId = this.generateSessionId();
        this.activities = [];
        this.batchSize = 10;
        this.batchTimer = null;
        this.batchInterval = 300000; // 5 minutes
        this.isDestroyed = false;

        this.setupEventListeners();
        this.startBatchTimer();
        this.logActivity('login', this.currentSessionId, 'home');
    }

    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    setupEventListeners() {
        // Track meaningful button clicks
        document.addEventListener('click', (e) => this.handleClick(e));

        // Track tab changes via custom event
        document.addEventListener('tabchange', (e) => {
            const tabName = (e.detail && e.detail.tabName) || 'unknown_tab';
            this.logActivity('tab_change', tabName, tabName);
        });

        // Track page unload (logout/close)
        window.addEventListener('beforeunload', () => {
            this.logActivity('logout', this.currentSessionId, this.getCurrentAppState());
            this.sendBatch(true);
        });

        // Track visibility changes
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.logActivity('app_minimized', '', this.getCurrentAppState());
            } else {
                this.logActivity('app_resumed', '', this.getCurrentAppState());
            }
        });
    }

    logActivity(activityType, activityDetail, appState) {
        if (this.isDestroyed) return;

        activityDetail = activityDetail || '';
        appState = appState || this.getCurrentAppState();

        this.activities.push({
            activity_type: activityType,
            activity_detail: String(activityDetail).substring(0, 500),
            session_id: this.currentSessionId,
            app_state: appState,
            metadata: {
                timestamp: new Date().toISOString(),
                timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
            }
        });

        if (this.activities.length >= this.batchSize) {
            this.sendBatch();
        }
    }

    handleClick(event) {
        let target = event.target;

        // Walk up to find meaningful clickable element
        while (target && target !== document.body) {
            if (target.tagName === 'BUTTON' || (target.tagName === 'A' && target.href) ||
                target.classList.contains('clickable') || target.classList.contains('tab-btn') ||
                target.getAttribute('role') === 'button') {
                const label = target.innerText || target.id || target.getAttribute('aria-label') || 'unknown';
                this.logActivity('button_click', label.substring(0, 100).trim(), this.getCurrentAppState());
                return;
            }
            target = target.parentElement;
        }
    }

    getCurrentAppState() {
        // Check active tab
        const activeTab = document.querySelector('.tab-content.active');
        if (activeTab && activeTab.id) {
            return activeTab.id.replace('Tab', '');
        }
        const activeBtn = document.querySelector('.tab-btn.active');
        if (activeBtn && activeBtn.id) {
            return activeBtn.id.replace('TabBtn', '');
        }
        return 'home';
    }

    startBatchTimer() {
        this.batchTimer = setInterval(() => {
            if (this.activities.length > 0) {
                this.sendBatch();
            }
        }, this.batchInterval);
    }

    sendBatch(urgent) {
        if (this.activities.length === 0) return;

        const batchToSend = this.activities.slice();
        this.activities = [];

        const payload = JSON.stringify({ activities: batchToSend });

        if (urgent && navigator.sendBeacon) {
            const blob = new Blob([payload], { type: 'application/json' });
            navigator.sendBeacon('/api/activity/log', blob);
            return;
        }

        fetch('/api/activity/log', {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: payload
        }).then(function(response) {
            if (!response.ok) {
                console.warn('Activity logging failed');
            }
        }).catch(function() {
            // Silently fail - activity logging should never break the app
        });
    }

    destroy() {
        this.isDestroyed = true;
        if (this.batchTimer) {
            clearInterval(this.batchTimer);
            this.batchTimer = null;
        }
        this.sendBatch(true);
    }
}

// Global reference - initialized after login
var activityLogger = null;
