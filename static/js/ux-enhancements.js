/**
 * Healing Space - Phase 4 UX Enhancements
 * Version: 1.0.0
 * Date: January 2026
 *
 * This file provides:
 * - Loading indicators
 * - Toast notifications
 * - Confirmation dialogs
 * - Onboarding wizard
 * - Privacy panel
 * - Accessibility enhancements
 * - Empathetic error messages
 * - Feature flags
 */

(function() {
    'use strict';

    // ============================================
    // CONFIGURATION & FEATURE FLAGS
    // ============================================
    const HealingSpaceUX = {
        config: {
            enableOnboarding: true,
            enableToasts: true,
            enableConfirmDialogs: true,
            enablePrivacyPanel: true,
            enableAccessibility: true,
            enableEmpatheticMessages: true,
            toastDuration: 5000,
            onboardingVersion: '1.0',
            debugMode: false
        },

        // Empathetic message templates
        messages: {
            // Error messages - friendly and supportive
            errors: {
                network: "We're having trouble connecting right now. Please check your internet connection and try again. We're here when you're ready.",
                server: "Something unexpected happened on our end. Don't worry, your data is safe. Please try again in a moment.",
                validation: "Some information needs a little adjustment. Please check the highlighted fields.",
                auth: "We couldn't verify your details. Please double-check and try again. If you've forgotten your password, we can help you reset it.",
                permission: "You don't have access to this feature yet. If you think this is a mistake, please contact your clinician.",
                timeout: "This is taking longer than expected. Please wait a moment or try again.",
                rateLimit: "You're moving quickly! Please take a brief pause and try again in a few moments.",
                generic: "Something didn't work as expected. Please try again, and if the problem continues, we're here to help."
            },

            // Success messages - warm and encouraging
            success: {
                saved: "Beautifully done! Your entry has been saved.",
                moodLogged: "Thank you for checking in with yourself today. Every moment of self-awareness matters.",
                messageSent: "Your message has been sent.",
                profileUpdated: "Your profile has been updated successfully.",
                passwordChanged: "Your password has been changed. You're all set!",
                loggedIn: "Welcome back! It's good to see you.",
                loggedOut: "You've been logged out safely. Take care!",
                entryDeleted: "Entry removed.",
                reportGenerated: "Your report is ready."
            },

            // Encouragement messages
            encouragement: [
                "You're doing great by taking time for yourself today.",
                "Every small step counts towards your wellbeing.",
                "It takes courage to reflect on how you're feeling.",
                "You're making progress, one day at a time.",
                "Thank you for trusting us with your journey.",
                "Remember: it's okay to have difficult days.",
                "Your commitment to self-care is inspiring."
            ],

            // Loading messages
            loading: {
                default: "Loading...",
                ai: "Thinking about what you shared...",
                insights: "Gathering your insights...",
                report: "Preparing your report...",
                saving: "Saving your entry...",
                connecting: "Connecting..."
            }
        },

        // State
        state: {
            onboardingComplete: false,
            toastQueue: [],
            activeDialogs: 0
        }
    };

    // ============================================
    // INITIALIZATION
    // ============================================
    function init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', onDOMReady);
        } else {
            onDOMReady();
        }
    }

    function onDOMReady() {
        log('Healing Space UX Enhancements initializing...');

        // Create DOM elements
        createToastContainer();
        createLoadingOverlay();
        createDialogContainer();
        createPrivacyPanel();
        createOnboardingWizard();

        // Setup accessibility
        if (HealingSpaceUX.config.enableAccessibility) {
            setupAccessibility();
        }

        // Check onboarding status
        if (HealingSpaceUX.config.enableOnboarding) {
            checkOnboardingStatus();
        }

        // Setup global error handler
        setupGlobalErrorHandler();

        // Expose API
        window.HealingSpaceUX = {
            showLoading,
            hideLoading,
            showToast,
            showConfirm,
            showOnboarding,
            showPrivacyPanel,
            hidePrivacyPanel,
            getEmpatheticError,
            getEmpatheticSuccess,
            getEncouragement,
            setConfig,
            config: HealingSpaceUX.config
        };

        log('UX Enhancements ready');
    }

    // ============================================
    // LOGGING
    // ============================================
    function log(...args) {
        if (HealingSpaceUX.config.debugMode) {
            console.log('[HealingSpaceUX]', ...args);
        }
    }

    // ============================================
    // LOADING INDICATORS
    // ============================================
    function createLoadingOverlay() {
        const overlay = document.createElement('div');
        overlay.id = 'hsLoadingOverlay';
        overlay.className = 'hs-loading-overlay';
        overlay.setAttribute('role', 'alert');
        overlay.setAttribute('aria-live', 'polite');
        overlay.innerHTML = `
            <div class="hs-loading-spinner" aria-hidden="true"></div>
            <div class="hs-loading-text" id="hsLoadingText">Loading...</div>
            <div class="hs-loading-subtext" id="hsLoadingSubtext"></div>
        `;
        document.body.appendChild(overlay);
    }

    function showLoading(message, subtext) {
        const overlay = document.getElementById('hsLoadingOverlay');
        const textEl = document.getElementById('hsLoadingText');
        const subtextEl = document.getElementById('hsLoadingSubtext');

        if (overlay) {
            textEl.textContent = message || HealingSpaceUX.messages.loading.default;
            subtextEl.textContent = subtext || '';
            overlay.classList.add('active');
        }
    }

    function hideLoading() {
        const overlay = document.getElementById('hsLoadingOverlay');
        if (overlay) {
            overlay.classList.remove('active');
        }
    }

    // ============================================
    // TOAST NOTIFICATIONS
    // ============================================
    function createToastContainer() {
        const container = document.createElement('div');
        container.id = 'hsToastContainer';
        container.className = 'hs-toast-container';
        container.setAttribute('role', 'region');
        container.setAttribute('aria-label', 'Notifications');
        container.setAttribute('aria-live', 'polite');
        document.body.appendChild(container);
    }

    function showToast(options) {
        if (!HealingSpaceUX.config.enableToasts) return;

        const defaults = {
            type: 'info', // success, warning, error, info
            title: '',
            message: '',
            duration: HealingSpaceUX.config.toastDuration,
            closable: true
        };

        const opts = { ...defaults, ...options };

        const icons = {
            success: '✓',
            warning: '⚠',
            error: '✕',
            info: 'ℹ'
        };

        const toast = document.createElement('div');
        toast.className = `hs-toast ${opts.type}`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <span class="hs-toast-icon" aria-hidden="true">${icons[opts.type]}</span>
            <div class="hs-toast-content">
                ${opts.title ? `<div class="hs-toast-title">${escapeHtml(opts.title)}</div>` : ''}
                <div class="hs-toast-message">${escapeHtml(opts.message)}</div>
            </div>
            ${opts.closable ? '<button class="hs-toast-close" aria-label="Close notification">&times;</button>' : ''}
        `;

        const container = document.getElementById('hsToastContainer');
        container.appendChild(toast);

        // Close button
        if (opts.closable) {
            toast.querySelector('.hs-toast-close').addEventListener('click', () => {
                removeToast(toast);
            });
        }

        // Auto remove
        if (opts.duration > 0) {
            setTimeout(() => removeToast(toast), opts.duration);
        }

        return toast;
    }

    function removeToast(toast) {
        toast.classList.add('exiting');
        setTimeout(() => toast.remove(), 300);
    }

    // ============================================
    // CONFIRMATION DIALOGS
    // ============================================
    function createDialogContainer() {
        const overlay = document.createElement('div');
        overlay.id = 'hsDialogOverlay';
        overlay.className = 'hs-dialog-overlay';
        overlay.setAttribute('role', 'dialog');
        overlay.setAttribute('aria-modal', 'true');
        overlay.innerHTML = `<div class="hs-dialog" id="hsDialog"></div>`;
        document.body.appendChild(overlay);

        // Close on overlay click
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                hideDialog();
            }
        });

        // Close on Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && HealingSpaceUX.state.activeDialogs > 0) {
                hideDialog();
            }
        });
    }

    function showConfirm(options) {
        if (!HealingSpaceUX.config.enableConfirmDialogs) {
            return Promise.resolve(true);
        }

        return new Promise((resolve) => {
            const defaults = {
                icon: '❓',
                title: 'Are you sure?',
                message: '',
                confirmText: 'Confirm',
                cancelText: 'Cancel',
                confirmClass: 'hs-dialog-btn-primary',
                dangerous: false
            };

            const opts = { ...defaults, ...options };
            if (opts.dangerous) {
                opts.confirmClass = 'hs-dialog-btn-danger';
            }

            const dialog = document.getElementById('hsDialog');
            dialog.innerHTML = `
                <div class="hs-dialog-icon" aria-hidden="true">${opts.icon}</div>
                <h3 class="hs-dialog-title">${escapeHtml(opts.title)}</h3>
                <p class="hs-dialog-message">${escapeHtml(opts.message)}</p>
                <div class="hs-dialog-actions">
                    <button class="hs-dialog-btn hs-dialog-btn-secondary" id="hsDialogCancel">${escapeHtml(opts.cancelText)}</button>
                    <button class="hs-dialog-btn ${opts.confirmClass}" id="hsDialogConfirm">${escapeHtml(opts.confirmText)}</button>
                </div>
            `;

            const overlay = document.getElementById('hsDialogOverlay');
            overlay.classList.add('active');
            HealingSpaceUX.state.activeDialogs++;

            // Focus the cancel button (safer default)
            setTimeout(() => {
                document.getElementById('hsDialogCancel').focus();
            }, 100);

            document.getElementById('hsDialogCancel').onclick = () => {
                hideDialog();
                resolve(false);
            };

            document.getElementById('hsDialogConfirm').onclick = () => {
                hideDialog();
                resolve(true);
            };
        });
    }

    function hideDialog() {
        const overlay = document.getElementById('hsDialogOverlay');
        overlay.classList.remove('active');
        HealingSpaceUX.state.activeDialogs = Math.max(0, HealingSpaceUX.state.activeDialogs - 1);
    }

    // ============================================
    // ONBOARDING WIZARD
    // ============================================
    function createOnboardingWizard() {
        const overlay = document.createElement('div');
        overlay.id = 'hsOnboardingOverlay';
        overlay.className = 'hs-onboarding-overlay';
        overlay.innerHTML = `
            <div class="hs-onboarding-container">
                <div class="hs-onboarding-header">
                    <div class="hs-onboarding-logo">🌿</div>
                    <h2 class="hs-onboarding-title">Welcome to Healing Space</h2>
                    <p class="hs-onboarding-subtitle">Your personal mental health companion</p>
                </div>

                <div class="hs-onboarding-progress">
                    <div class="hs-onboarding-step active" data-step="1"></div>
                    <div class="hs-onboarding-step" data-step="2"></div>
                    <div class="hs-onboarding-step" data-step="3"></div>
                    <div class="hs-onboarding-step" data-step="4"></div>
                    <div class="hs-onboarding-step" data-step="5"></div>
                </div>

                <div class="hs-onboarding-content">
                    <!-- Slide 1: Welcome -->
                    <div class="hs-onboarding-slide active" data-slide="1">
                        <h3>We're glad you're here</h3>
                        <p>Healing Space is designed to support your mental health journey with compassion, privacy, and evidence-based tools.</p>
                        <div class="hs-supportive-message">
                            <p>Taking care of your mental health is an act of courage. Whatever brought you here, we're honoured to be part of your journey.</p>
                        </div>
                    </div>

                    <!-- Slide 2: Features -->
                    <div class="hs-onboarding-slide" data-slide="2">
                        <h3>What you can do here</h3>
                        <ul class="hs-feature-list">
                            <li>
                                <span class="hs-feature-icon">💬</span>
                                <div class="hs-feature-text">
                                    <strong>AI Therapy Chat</strong>
                                    <span>Talk to a supportive AI companion anytime</span>
                                </div>
                            </li>
                            <li>
                                <span class="hs-feature-icon">📊</span>
                                <div class="hs-feature-text">
                                    <strong>Mood Tracking</strong>
                                    <span>Log your emotions, sleep, and wellness</span>
                                </div>
                            </li>
                            <li>
                                <span class="hs-feature-icon">✨</span>
                                <div class="hs-feature-text">
                                    <strong>Gratitude Journal</strong>
                                    <span>Cultivate positivity through daily reflections</span>
                                </div>
                            </li>
                            <li>
                                <span class="hs-feature-icon">🧠</span>
                                <div class="hs-feature-text">
                                    <strong>CBT Tools</strong>
                                    <span>Evidence-based cognitive behavioural exercises</span>
                                </div>
                            </li>
                            <li>
                                <span class="hs-feature-icon">📈</span>
                                <div class="hs-feature-text">
                                    <strong>Insights</strong>
                                    <span>Understand your patterns over time</span>
                                </div>
                            </li>
                        </ul>
                    </div>

                    <!-- Slide 3: Privacy -->
                    <div class="hs-onboarding-slide" data-slide="3">
                        <h3>Your privacy matters</h3>
                        <p>We take your privacy seriously. Here's what you should know:</p>
                        <div class="hs-privacy-highlight">
                            <p><strong>🔒 Your data is encrypted</strong> - All personal information is protected with strong encryption.</p>
                        </div>
                        <ul class="hs-feature-list">
                            <li>
                                <span class="hs-feature-icon">👤</span>
                                <div class="hs-feature-text">
                                    <strong>Only you and your clinician</strong>
                                    <span>can see your entries (if you have one assigned)</span>
                                </div>
                            </li>
                            <li>
                                <span class="hs-feature-icon">🗑️</span>
                                <div class="hs-feature-text">
                                    <strong>You control your data</strong>
                                    <span>Request deletion anytime from Settings</span>
                                </div>
                            </li>
                            <li>
                                <span class="hs-feature-icon">📤</span>
                                <div class="hs-feature-text">
                                    <strong>Export your data</strong>
                                    <span>Download your information in standard formats</span>
                                </div>
                            </li>
                        </ul>
                    </div>

                    <!-- Slide 4: Crisis Support -->
                    <div class="hs-onboarding-slide" data-slide="4">
                        <h3>We're here for difficult moments</h3>
                        <p>If you're ever feeling overwhelmed or in crisis, please know that support is available.</p>
                        <div class="hs-crisis-banner">
                            <span class="hs-crisis-banner-icon">🆘</span>
                            <div class="hs-crisis-banner-content">
                                <div class="hs-crisis-banner-title">Crisis Resources</div>
                                <div class="hs-crisis-banner-text">
                                    If you're in immediate danger, please contact emergency services or a crisis helpline:
                                    <br><br>
                                    <strong>UK:</strong> Samaritans - 116 123<br>
                                    <strong>US:</strong> 988 Suicide & Crisis Lifeline<br>
                                    <strong>International:</strong> <a href="https://findahelpline.com" target="_blank" class="hs-crisis-banner-link">findahelpline.com</a>
                                </div>
                            </div>
                        </div>
                        <p style="margin-top: 16px; font-size: 0.9rem; color: #666;">
                            While Healing Space provides supportive tools, it's not a replacement for professional mental health care.
                        </p>
                    </div>

                    <!-- Slide 5: Get Started -->
                    <div class="hs-onboarding-slide" data-slide="5">
                        <h3>You're all set!</h3>
                        <p>Here are some suggestions to get started:</p>
                        <ul class="hs-feature-list">
                            <li>
                                <span class="hs-feature-icon">1️⃣</span>
                                <div class="hs-feature-text">
                                    <strong>Log your mood</strong>
                                    <span>Start by checking in with how you're feeling today</span>
                                </div>
                            </li>
                            <li>
                                <span class="hs-feature-icon">2️⃣</span>
                                <div class="hs-feature-text">
                                    <strong>Say hello to your AI companion</strong>
                                    <span>Open the Therapy Chat and share what's on your mind</span>
                                </div>
                            </li>
                            <li>
                                <span class="hs-feature-icon">3️⃣</span>
                                <div class="hs-feature-text">
                                    <strong>Explore at your own pace</strong>
                                    <span>There's no rush - use what feels right for you</span>
                                </div>
                            </li>
                        </ul>
                        <div class="hs-supportive-message" style="margin-top: 20px;">
                            <p>Remember: every journey begins with a single step. You've already taken yours by being here. 💚</p>
                        </div>
                    </div>
                </div>

                <div class="hs-onboarding-footer">
                    <button class="hs-onboarding-skip" id="hsOnboardingSkip">Skip tour</button>
                    <div class="hs-onboarding-nav">
                        <button class="btn btn-secondary" id="hsOnboardingPrev" style="display: none;">Back</button>
                        <button class="btn" id="hsOnboardingNext">Next</button>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(overlay);

        // Setup navigation
        setupOnboardingNavigation();
    }

    let currentOnboardingSlide = 1;
    const totalOnboardingSlides = 5;

    function setupOnboardingNavigation() {
        document.getElementById('hsOnboardingNext').addEventListener('click', () => {
            if (currentOnboardingSlide < totalOnboardingSlides) {
                goToOnboardingSlide(currentOnboardingSlide + 1);
            } else {
                completeOnboarding();
            }
        });

        document.getElementById('hsOnboardingPrev').addEventListener('click', () => {
            if (currentOnboardingSlide > 1) {
                goToOnboardingSlide(currentOnboardingSlide - 1);
            }
        });

        document.getElementById('hsOnboardingSkip').addEventListener('click', () => {
            completeOnboarding();
        });
    }

    function goToOnboardingSlide(slideNum) {
        currentOnboardingSlide = slideNum;

        // Update slides
        document.querySelectorAll('.hs-onboarding-slide').forEach(slide => {
            slide.classList.remove('active');
        });
        document.querySelector(`.hs-onboarding-slide[data-slide="${slideNum}"]`).classList.add('active');

        // Update progress
        document.querySelectorAll('.hs-onboarding-step').forEach(step => {
            const stepNum = parseInt(step.dataset.step);
            step.classList.remove('active', 'completed');
            if (stepNum === slideNum) {
                step.classList.add('active');
            } else if (stepNum < slideNum) {
                step.classList.add('completed');
            }
        });

        // Update buttons
        const prevBtn = document.getElementById('hsOnboardingPrev');
        const nextBtn = document.getElementById('hsOnboardingNext');

        prevBtn.style.display = slideNum > 1 ? 'inline-block' : 'none';
        nextBtn.textContent = slideNum === totalOnboardingSlides ? "Let's begin!" : 'Next';
    }

    function showOnboarding() {
        currentOnboardingSlide = 1;
        goToOnboardingSlide(1);
        document.getElementById('hsOnboardingOverlay').classList.add('active');
    }

    function completeOnboarding() {
        document.getElementById('hsOnboardingOverlay').classList.remove('active');
        HealingSpaceUX.state.onboardingComplete = true;

        // Save to localStorage
        const onboardingData = {
            completed: true,
            version: HealingSpaceUX.config.onboardingVersion,
            completedAt: new Date().toISOString()
        };
        localStorage.setItem('hsOnboarding', JSON.stringify(onboardingData));

        // Show welcome toast
        showToast({
            type: 'success',
            title: 'Welcome!',
            message: getEncouragement()
        });

        // Log for analytics
        logUXEvent('onboarding_completed', { version: HealingSpaceUX.config.onboardingVersion });
    }

    function checkOnboardingStatus() {
        const saved = localStorage.getItem('hsOnboarding');
        if (saved) {
            const data = JSON.parse(saved);
            if (data.completed && data.version === HealingSpaceUX.config.onboardingVersion) {
                HealingSpaceUX.state.onboardingComplete = true;
                return;
            }
        }

        // Show onboarding after login (hook into completeLogin)
        const originalCompleteLogin = window.completeLogin;
        if (typeof originalCompleteLogin === 'function') {
            window.completeLogin = function(data) {
                originalCompleteLogin.call(this, data);

                // Check if this is a new user (first login)
                setTimeout(() => {
                    if (!HealingSpaceUX.state.onboardingComplete && data.role === 'user') {
                        showOnboarding();
                    }
                }, 500);
            };
        }
    }

    // ============================================
    // PRIVACY PANEL
    // ============================================
    function createPrivacyPanel() {
        const panel = document.createElement('div');
        panel.id = 'hsPrivacyPanel';
        panel.className = 'hs-privacy-panel';
        panel.setAttribute('role', 'dialog');
        panel.setAttribute('aria-label', 'Privacy Information');
        panel.innerHTML = `
            <div class="hs-privacy-header">
                <h3>🔒 Your Privacy</h3>
                <button class="hs-privacy-close" id="hsPrivacyClose" aria-label="Close privacy panel">&times;</button>
            </div>
            <div class="hs-privacy-content">
                <div class="hs-privacy-section">
                    <h4>📋 What we collect</h4>
                    <p>We only collect information necessary to provide you with mental health support:</p>
                    <ul>
                        <li>Account information (username, email)</li>
                        <li>Mood logs and journal entries you create</li>
                        <li>Chat conversations with the AI companion</li>
                        <li>Clinical assessments you complete</li>
                    </ul>
                </div>

                <div class="hs-privacy-section">
                    <h4>👁️ Who can see your data</h4>
                    <div class="hs-privacy-highlight">
                        <p><strong>Your data is private.</strong> Only you can see your entries. If you have an assigned clinician, they can view your data to provide better care - but only with your approval.</p>
                    </div>
                </div>

                <div class="hs-privacy-section">
                    <h4>🔐 How we protect it</h4>
                    <ul>
                        <li>All data is encrypted in transit and at rest</li>
                        <li>Sensitive fields use additional encryption</li>
                        <li>We follow healthcare data protection standards</li>
                        <li>Regular security audits are performed</li>
                    </ul>
                </div>

                <div class="hs-privacy-section">
                    <h4>⏱️ How long we keep it</h4>
                    <p>Your data is kept as long as you have an active account. You can request deletion of your data at any time through Settings, or by contacting support.</p>
                </div>

                <div class="hs-privacy-section">
                    <h4>📤 Your rights</h4>
                    <ul>
                        <li><strong>Access:</strong> Download all your data anytime</li>
                        <li><strong>Correction:</strong> Edit your information</li>
                        <li><strong>Deletion:</strong> Request removal of your data</li>
                        <li><strong>Portability:</strong> Export in standard formats (CSV, FHIR)</li>
                    </ul>
                </div>

                <div class="hs-privacy-section">
                    <h4>💡 AI & Your Data</h4>
                    <p>Our AI companion uses your conversation to provide relevant support. Your conversations are <strong>not used to train AI models</strong> and are kept confidential.</p>
                </div>
            </div>
        `;
        document.body.appendChild(panel);

        document.getElementById('hsPrivacyClose').addEventListener('click', hidePrivacyPanel);

        // Close on click outside
        document.addEventListener('click', (e) => {
            const panel = document.getElementById('hsPrivacyPanel');
            if (panel.classList.contains('active') && !panel.contains(e.target)) {
                hidePrivacyPanel();
            }
        });
    }

    function showPrivacyPanel() {
        document.getElementById('hsPrivacyPanel').classList.add('active');
    }

    function hidePrivacyPanel() {
        document.getElementById('hsPrivacyPanel').classList.remove('active');
    }

    // ============================================
    // ACCESSIBILITY ENHANCEMENTS
    // ============================================
    function setupAccessibility() {
        // Add skip link
        const skipLink = document.createElement('a');
        skipLink.href = '#main-content';
        skipLink.className = 'skip-to-main';
        skipLink.textContent = 'Skip to main content';
        document.body.insertBefore(skipLink, document.body.firstChild);

        // Add main content landmark
        const mainContent = document.querySelector('.main-content');
        if (mainContent) {
            mainContent.id = 'main-content';
            mainContent.setAttribute('role', 'main');
            mainContent.setAttribute('tabindex', '-1');
        }

        // Add ARIA labels to navigation
        const sidebar = document.querySelector('.sidebar');
        if (sidebar) {
            sidebar.setAttribute('role', 'navigation');
            sidebar.setAttribute('aria-label', 'Main navigation');
        }

        // Setup keyboard navigation for tabs
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.setAttribute('role', 'tab');
        });

        // Add live region for dynamic content
        const liveRegion = document.createElement('div');
        liveRegion.id = 'hsLiveRegion';
        liveRegion.className = 'sr-only';
        liveRegion.setAttribute('aria-live', 'polite');
        liveRegion.setAttribute('aria-atomic', 'true');
        document.body.appendChild(liveRegion);

        // Load user accessibility preferences
        loadAccessibilityPreferences();
    }

    function loadAccessibilityPreferences() {
        const prefs = localStorage.getItem('hsAccessibility');
        if (prefs) {
            const settings = JSON.parse(prefs);
            applyAccessibilitySettings(settings);
        }
    }

    function applyAccessibilitySettings(settings) {
        if (settings.fontScale) {
            document.documentElement.setAttribute('data-font-scale', settings.fontScale);
        }
        if (settings.highContrast) {
            document.documentElement.setAttribute('data-high-contrast', 'true');
        }
        if (settings.reducedMotion) {
            document.documentElement.setAttribute('data-reduced-motion', 'true');
        }
    }

    function announceToScreenReader(message) {
        const region = document.getElementById('hsLiveRegion');
        if (region) {
            region.textContent = message;
            setTimeout(() => { region.textContent = ''; }, 1000);
        }
    }

    // ============================================
    // EMPATHETIC MESSAGES
    // ============================================
    function getEmpatheticError(errorType, fallback) {
        if (!HealingSpaceUX.config.enableEmpatheticMessages) {
            return fallback || 'An error occurred.';
        }
        return HealingSpaceUX.messages.errors[errorType] || HealingSpaceUX.messages.errors.generic;
    }

    function getEmpatheticSuccess(successType, fallback) {
        if (!HealingSpaceUX.config.enableEmpatheticMessages) {
            return fallback || 'Success!';
        }
        return HealingSpaceUX.messages.success[successType] || fallback || 'Done!';
    }

    function getEncouragement() {
        const messages = HealingSpaceUX.messages.encouragement;
        return messages[Math.floor(Math.random() * messages.length)];
    }

    // ============================================
    // GLOBAL ERROR HANDLER
    // ============================================
    function setupGlobalErrorHandler() {
        // Intercept fetch to add friendly error handling
        const originalFetch = window.fetch;
        window.fetch = async function(...args) {
            try {
                const response = await originalFetch.apply(this, args);

                // Handle rate limiting with friendly message
                if (response.status === 429) {
                    showToast({
                        type: 'warning',
                        title: 'Please slow down',
                        message: getEmpatheticError('rateLimit')
                    });
                }

                return response;
            } catch (error) {
                // Network error
                if (error.name === 'TypeError' && error.message.includes('fetch')) {
                    showToast({
                        type: 'error',
                        title: 'Connection issue',
                        message: getEmpatheticError('network')
                    });
                }
                throw error;
            }
        };
    }

    // ============================================
    // UTILITY FUNCTIONS
    // ============================================
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function setConfig(key, value) {
        if (HealingSpaceUX.config.hasOwnProperty(key)) {
            HealingSpaceUX.config[key] = value;
        }
    }

    function logUXEvent(eventName, data) {
        // Log UX events for analytics/debugging
        log('UX Event:', eventName, data);

        // Could send to server for analytics
        // fetch('/api/analytics/ux', { method: 'POST', body: JSON.stringify({ event: eventName, data }) });
    }

    // Initialize
    init();
})();
