/**
 * Healing Space - Messaging System Frontend Module
 * 
 * Comprehensive messaging interface for patients, clinicians, and admins
 * Features:
 * - Direct messaging
 * - Group conversations
 * - Message templates
 * - Message scheduling
 * - User blocking
 * - Notifications
 * - Search functionality
 * - Real-time updates (via polling)
 */

class MessagingSystem {
    constructor(config = {}) {
        this.apiBase = config.apiBase || '/api/messages';
        this.csrfToken = config.csrfToken || this.getCsrfToken();
        this.userRole = config.userRole || 'user';
        this.username = config.username || null;
        this.pollInterval = config.pollInterval || 5000; // 5 seconds
        this.unreadCount = 0;
        this.currentConversation = null;
        this.pollTimer = null;
        this.selectedTab = 'inbox';
        this.templates = [];
        this.blockedUsers = [];
        
        this.init();
    }

    /**
     * Initialize messaging system
     */
    init() {
                this.accessibleTabs = ['inbox', 'sent', 'compose'];
                if (this.userRole === 'clinician' || this.userRole === 'developer') {
                    this.accessibleTabs.push('group', 'broadcast', 'analytics');
                }
        this.setupEventListeners();
        this.loadInbox();
        this.startPolling();
        this.loadBlockedUsers();
        this.loadTemplates();
    }

    /**
     * Get CSRF token from cookie
     */
    getCsrfToken() {
        const name = 'csrf_token=';
        const decodedCookie = decodeURIComponent(document.cookie);
        const cookieArray = decodedCookie.split(';');
        for (let cookie of cookieArray) {
            cookie = cookie.trim();
            if (cookie.indexOf(name) === 0) {
                return cookie.substring(name.length);
            }
        }
        return '';
    }

    /**
     * Setup event listeners for messaging UI
     */
    setupEventListeners() {
        // Tab switching
        document.querySelectorAll('[data-messaging-tab]').forEach(tab => {
            tab.addEventListener('click', (e) => this.switchTab(e.target.dataset.messagingTab));
        });

        // Send message button
        const sendBtn = document.getElementById('send-message-btn');
        if (sendBtn) {
            sendBtn.addEventListener('click', () => this.sendMessage());
        }

        // Message input - send on Enter
        const messageInput = document.getElementById('message-input');
        if (messageInput) {
            messageInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && e.ctrlKey) {
                    this.sendMessage();
                }
            });
        }

        // Search messages
        const searchBtn = document.getElementById('search-messages-btn');
        if (searchBtn) {
                    // Accessibility: Announce inbox loaded
                    this.announce('Inbox loaded.');
            searchBtn.addEventListener('click', () => this.searchMessages());
        }

        // Create group button
        const createGroupBtn = document.getElementById('create-group-btn');
        if (createGroupBtn) {
            createGroupBtn.addEventListener('click', () => this.showCreateGroupModal());
        }

        // Schedule message button
        const scheduleBtn = document.getElementById('schedule-message-btn');
        if (scheduleBtn) {
            scheduleBtn.addEventListener('click', () => this.showScheduleModal());
        }

        // Block user button
        const blockBtn = document.getElementById('block-user-btn');
        if (blockBtn) {
            blockBtn.addEventListener('click', () => this.showBlockModal());
        }
    }

                    this.announce('Sent messages loaded.');
    /**
     * Switch between tabs (inbox, sent, templates, etc.)
     */
    switchTab(tabName) {
        this.selectedTab = tabName;
        
        // Update UI
        document.querySelectorAll('[data-messaging-tab]').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelector(`[data-messaging-tab="${tabName}"]`).classList.add('active');

        // Hide all panels
        document.querySelectorAll('[data-messaging-panel]').forEach(panel => {
                    badge.setAttribute('aria-label', `${this.unreadCount} unread messages`);
            panel.style.display = 'none';
        });

        // Show selected panel
        const panel = document.querySelector(`[data-messaging-panel="${tabName}"]`);
        if (panel) {
            panel.style.display = 'block';
        }
                this.announce(message);

        // Load appropriate content
        switch (tabName) {
            case 'inbox':
                this.loadInbox();
                break;
            case 'sent':
                this.announce(message);
                this.loadSentMessages();
                break;
            announce(message) {
                // Accessibility: Announce messages to screen readers
                let liveRegion = document.getElementById('messaging-live-region');
                if (!liveRegion) {
                    liveRegion = document.createElement('div');
                    liveRegion.id = 'messaging-live-region';
                    liveRegion.setAttribute('aria-live', 'polite');
                    liveRegion.style.position = 'absolute';
                    liveRegion.style.left = '-9999px';
                    document.body.appendChild(liveRegion);
                }
                liveRegion.textContent = message;
            case 'templates':
                this.loadTemplates();
                break;
            case 'scheduled':
                this.loadScheduledMessages();
                break;
            case 'blocked':
                this.loadBlockedUsers();
                break;
        }
    }

    /**
     * Load inbox conversations
     */
    async loadInbox() {
        try {
            const response = await fetch(`${this.apiBase}/inbox?page=1&limit=50`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) throw new Error('Failed to load inbox');

            const data = await response.json();
            this.unreadCount = data.total_unread;
            this.updateUnreadBadge();
            this.renderConversationsList(data.conversations);
        } catch (error) {
            console.error('Error loading inbox:', error);
            this.showError('Failed to load inbox');
        }
    }

    /**
     * Load sent messages
     */
    async loadSentMessages() {
        try {
            const response = await fetch(`${this.apiBase}/sent`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) throw new Error('Failed to load sent messages');

            const data = await response.json();
            this.renderMessagesList(data.messages, 'sent');
        } catch (error) {
            console.error('Error loading sent messages:', error);
            this.showError('Failed to load sent messages');
        }
    }

    /**
     * Load message templates
     */
    async loadTemplates() {
        try {
            const response = await fetch(`${this.apiBase}/templates`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) throw new Error('Failed to load templates');

            const data = await response.json();
            this.templates = data.templates || [];
            this.renderTemplatesList(this.templates);
        } catch (error) {
            console.error('Error loading templates:', error);
            this.showError('Failed to load templates');
        }
    }

    /**
     * Load scheduled messages
     */
    async loadScheduledMessages() {
        try {
            const response = await fetch(`${this.apiBase}/scheduled`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) throw new Error('Failed to load scheduled messages');

            const data = await response.json();
            this.renderScheduledList(data.scheduled_messages || []);
        } catch (error) {
            console.error('Error loading scheduled messages:', error);
            this.showError('Failed to load scheduled messages');
        }
    }

    /**
     * Load blocked users
     */
    async loadBlockedUsers() {
        try {
            const response = await fetch(`${this.apiBase}/blocked`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) throw new Error('Failed to load blocked users');

            const data = await response.json();
            this.blockedUsers = data.blocked_users || [];
            this.renderBlockedUsersList(this.blockedUsers);
        } catch (error) {
            console.error('Error loading blocked users:', error);
        }
    }

    /**
     * Load full conversation with a user
     */
    async loadConversation(withUser) {
        try {
            const response = await fetch(`${this.apiBase}/conversation/${withUser}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) throw new Error('Failed to load conversation');

            const data = await response.json();
            this.currentConversation = {
                withUser: withUser,
                messages: data.messages || []
            };
            this.renderConversationThread(data.messages);
        } catch (error) {
            console.error('Error loading conversation:', error);
            this.showError('Failed to load conversation');
        }
    }

    /**
     * Send a direct message
     */
    async sendMessage() {
        const recipientInput = document.getElementById('recipient-input');
        const subjectInput = document.getElementById('subject-input');
        const messageInput = document.getElementById('message-input');

        const recipient = recipientInput ? recipientInput.value.trim() : null;
        const subject = subjectInput ? subjectInput.value.trim() : '';
        const content = messageInput ? messageInput.value.trim() : '';

        if (!recipient || !content) {
            this.showError('Please enter recipient and message');
            return;
        }

        try {
            const response = await fetch(`${this.apiBase}/send`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-Token': this.csrfToken
                },
                body: JSON.stringify({
                    recipient: recipient,
                    subject: subject,
                    content: content
                })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to send message');
            }

            const data = await response.json();
            this.showSuccess('Message sent!');
            messageInput.value = '';
            subjectInput.value = '';
            this.loadInbox();
        } catch (error) {
            console.error('Error sending message:', error);
            this.showError(error.message);
        }
    }

    /**
     * Search messages
     */
    async searchMessages() {
        const searchInput = document.getElementById('search-input');
        const query = searchInput ? searchInput.value.trim() : '';

        if (!query || query.length < 2) {
            this.showError('Search query must be at least 2 characters');
            return;
        }

        try {
            const response = await fetch(`${this.apiBase}/search?q=${encodeURIComponent(query)}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) throw new Error('Search failed');

            const data = await response.json();
            this.renderSearchResults(data.results || []);
        } catch (error) {
            console.error('Error searching messages:', error);
            this.showError('Search failed');
        }
    }

    /**
     * Schedule a message
     */
    async scheduleMessage(recipient, content, subject, scheduledFor) {
        try {
            const response = await fetch(`${this.apiBase}/scheduled`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-Token': this.csrfToken
                },
                body: JSON.stringify({
                    recipient: recipient,
                    content: content,
                    subject: subject,
                    scheduled_for: scheduledFor
                })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to schedule message');
            }

            this.showSuccess('Message scheduled!');
            this.loadScheduledMessages();
        } catch (error) {
            console.error('Error scheduling message:', error);
            this.showError(error.message);
        }
    }

    /**
     * Block a user
     */
    async blockUser(usernameToBlock, reason = '') {
        try {
            const response = await fetch(`${this.apiBase}/block/${usernameToBlock}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-Token': this.csrfToken
                },
                body: JSON.stringify({
                    reason: reason
                })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to block user');
            }

            this.showSuccess('User blocked');
            this.blockedUsers.push(usernameToBlock);
            this.loadBlockedUsers();
        } catch (error) {
            console.error('Error blocking user:', error);
            this.showError(error.message);
        }
    }

    /**
     * Unblock a user
     */
    async unblockUser(usernameToUnblock) {
        try {
            const response = await fetch(`${this.apiBase}/block/${usernameToUnblock}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-Token': this.csrfToken
                }
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to unblock user');
            }

            this.showSuccess('User unblocked');
            this.blockedUsers = this.blockedUsers.filter(u => u !== usernameToUnblock);
            this.loadBlockedUsers();
        } catch (error) {
            console.error('Error unblocking user:', error);
            this.showError(error.message);
        }
    }

    /**
     * Create a message template
     */
    async createTemplate(name, content, category, isPublic) {
        try {
            const response = await fetch(`${this.apiBase}/templates`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-Token': this.csrfToken
                },
                body: JSON.stringify({
                    name: name,
                    content: content,
                    category: category,
                    is_public: isPublic
                })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to create template');
            }

            this.showSuccess('Template created!');
            this.loadTemplates();
        } catch (error) {
            console.error('Error creating template:', error);
            this.showError(error.message);
        }
    }

    /**
     * Create group conversation
     */
    async createGroupConversation(subject, members) {
        try {
            const response = await fetch(`${this.apiBase}/group/create`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-Token': this.csrfToken
                },
                body: JSON.stringify({
                    subject: subject,
                    members: members
                })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to create group');
            }

            const data = await response.json();
            this.showSuccess('Group created!');
            this.loadInbox();
            return data.conversation_id;
        } catch (error) {
            console.error('Error creating group:', error);
            this.showError(error.message);
        }
    }

    // ============= UI Rendering Methods =============

    /**
     * Render conversations list
     */
    renderConversationsList(conversations) {
        const container = document.getElementById('conversations-list');
        if (!container) return;

        if (conversations.length === 0) {
            container.innerHTML = '<div class="empty-state">No conversations yet</div>';
            return;
        }

        const html = conversations.map(conv => `
            <div class="conversation-item" data-user="${conv.with_user}">
                <div class="conversation-header">
                    <span class="conversation-user">${this.escapeHtml(conv.with_user)}</span>
                    ${conv.unread_count > 0 ? `<span class="badge unread">${conv.unread_count}</span>` : ''}
                </div>
                <div class="conversation-preview">${this.escapeHtml(conv.last_message || 'No messages yet')}</div>
                <div class="conversation-time">${this.formatTime(conv.last_message_time)}</div>
            </div>
        `).join('');

        container.innerHTML = html;

        // Add click handlers
        container.querySelectorAll('.conversation-item').forEach(item => {
            item.addEventListener('click', () => {
                const user = item.dataset.user;
                this.loadConversation(user);
            });
        });
    }

    /**
     * Render conversation thread
     */
    renderConversationThread(messages) {
        const container = document.getElementById('conversation-thread');
        if (!container) return;

        const html = messages.map(msg => `
            <div class="message ${msg.sender === this.username ? 'sent' : 'received'}">
                <div class="message-sender">${this.escapeHtml(msg.sender)}</div>
                <div class="message-content">${this.escapeHtml(msg.content)}</div>
                <div class="message-time">${this.formatTime(msg.sent_at)}</div>
                ${msg.is_read ? '<div class="message-read-status">✓ Read</div>' : ''}
            </div>
        `).join('');

        container.innerHTML = html;
        container.scrollTop = container.scrollHeight;
    }

    /**
     * Render messages list
     */
    renderMessagesList(messages, type) {
        const container = document.getElementById('messages-list');
        if (!container) return;

        if (messages.length === 0) {
            container.innerHTML = `<div class="empty-state">No ${type} messages</div>`;
            return;
        }

        const html = messages.map(msg => `
            <div class="message-item">
                <div class="message-header">
                    <span class="message-participant">${this.escapeHtml(type === 'sent' ? msg.recipient : msg.sender)}</span>
                    <span class="message-time">${this.formatTime(msg.sent_at)}</span>
                </div>
                ${msg.subject ? `<div class="message-subject"><strong>Subject:</strong> ${this.escapeHtml(msg.subject)}</div>` : ''}
                <div class="message-preview">${this.escapeHtml(msg.content)}</div>
            </div>
        `).join('');

        container.innerHTML = html;
    }

    /**
     * Render templates list
     */
    renderTemplatesList(templates) {
        const container = document.getElementById('templates-list');
        if (!container) return;

        if (templates.length === 0) {
            container.innerHTML = '<div class="empty-state">No templates yet. Create one to get started!</div>';
            return;
        }

        const html = templates.map(template => `
            <div class="template-item" data-id="${template.id}">
                <div class="template-header">
                    <span class="template-name">${this.escapeHtml(template.name)}</span>
                    ${template.is_public ? '<span class="badge public">Public</span>' : '<span class="badge private">Private</span>'}
                </div>
                <div class="template-content">${this.escapeHtml(template.content.substring(0, 100))}...</div>
                <div class="template-actions">
                    <button class="btn-small use-template" data-id="${template.id}">Use</button>
                    <button class="btn-small edit-template" data-id="${template.id}">Edit</button>
                    <button class="btn-small delete-template" data-id="${template.id}">Delete</button>
                </div>
            </div>
        `).join('');

        container.innerHTML = html;

        // Add event listeners
        container.querySelectorAll('.use-template').forEach(btn => {
            btn.addEventListener('click', (e) => this.showUseTemplateModal(e.target.dataset.id));
        });
        
        container.querySelectorAll('.delete-template').forEach(btn => {
            btn.addEventListener('click', (e) => this.deleteTemplate(e.target.dataset.id));
        });
    }

    /**
     * Render scheduled messages list
     */
    renderScheduledList(messages) {
        const container = document.getElementById('scheduled-list');
        if (!container) return;

        if (messages.length === 0) {
            container.innerHTML = '<div class="empty-state">No scheduled messages</div>';
            return;
        }

        const html = messages.map(msg => `
            <div class="scheduled-item" data-id="${msg.message_id}">
                <div class="scheduled-header">
                    <span class="scheduled-recipient">${this.escapeHtml(msg.recipient)}</span>
                    <span class="scheduled-time">Scheduled: ${this.formatTime(msg.scheduled_for)}</span>
                </div>
                <div class="scheduled-preview">${this.escapeHtml(msg.content)}</div>
                <div class="scheduled-actions">
                    <button class="btn-small cancel-scheduled" data-id="${msg.message_id}">Cancel</button>
                </div>
            </div>
        `).join('');

        container.innerHTML = html;

        container.querySelectorAll('.cancel-scheduled').forEach(btn => {
            btn.addEventListener('click', (e) => this.cancelScheduledMessage(e.target.dataset.id));
        });
    }

    /**
     * Render blocked users list
     */
    renderBlockedUsersList(blockedUsers) {
        const container = document.getElementById('blocked-list');
        if (!container) return;

        if (blockedUsers.length === 0) {
            container.innerHTML = '<div class="empty-state">No blocked users</div>';
            return;
        }

        const html = blockedUsers.map(user => `
            <div class="blocked-user-item" data-user="${user.blocked_username}">
                <div class="blocked-user-header">
                    <span class="blocked-username">${this.escapeHtml(user.blocked_username)}</span>
                    ${user.reason ? `<span class="blocked-reason">Reason: ${this.escapeHtml(user.reason)}</span>` : ''}
                </div>
                <div class="blocked-user-actions">
                    <button class="btn-small unblock-user" data-user="${user.blocked_username}">Unblock</button>
                </div>
            </div>
        `).join('');

        container.innerHTML = html;

        container.querySelectorAll('.unblock-user').forEach(btn => {
            btn.addEventListener('click', (e) => this.unblockUser(e.target.dataset.user));
        });
    }

    /**
     * Render search results
     */
    renderSearchResults(results) {
        const container = document.getElementById('search-results');
        if (!container) return;

        if (results.length === 0) {
            container.innerHTML = '<div class="empty-state">No results found</div>';
            return;
        }

        const html = results.map(msg => `
            <div class="search-result-item">
                <div class="result-header">
                    <span class="result-user">${this.escapeHtml(msg.sender)}</span>
                    <span class="result-time">${this.formatTime(msg.sent_at)}</span>
                </div>
                ${msg.subject ? `<div class="result-subject">${this.escapeHtml(msg.subject)}</div>` : ''}
                <div class="result-content">${this.escapeHtml(msg.content)}</div>
            </div>
        `).join('');

        container.innerHTML = html;
    }

    // ============= Modal Methods =============

    /**
     * Show create group modal
     */
    showCreateGroupModal() {
        // Implementation for modal UI
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Create Group Conversation</h3>
                    <button class="close-modal">&times;</button>
                </div>
                <div class="modal-body">
                    <input type="text" id="group-subject" placeholder="Group name" maxlength="255">
                    <textarea id="group-members" placeholder="Enter usernames separated by commas" rows="4"></textarea>
                </div>
                <div class="modal-footer">
                    <button class="btn-primary" id="create-group-confirm">Create</button>
                    <button class="btn-secondary" id="create-group-cancel">Cancel</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);

        document.getElementById('create-group-confirm').addEventListener('click', async () => {
            const subject = document.getElementById('group-subject').value;
            const membersStr = document.getElementById('group-members').value;
            const members = membersStr.split(',').map(m => m.trim()).filter(m => m);
            
            if (subject && members.length >= 2) {
                await this.createGroupConversation(subject, members);
                modal.remove();
            }
        });

        document.getElementById('create-group-cancel').addEventListener('click', () => modal.remove());
        document.querySelector('.close-modal').addEventListener('click', () => modal.remove());
    }

    /**
     * Show schedule modal
     */
    showScheduleModal() {
        // Implementation for schedule modal
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Schedule Message</h3>
                    <button class="close-modal">&times;</button>
                </div>
                <div class="modal-body">
                    <input type="text" id="schedule-recipient" placeholder="Recipient username" maxlength="255">
                    <input type="datetime-local" id="schedule-datetime">
                    <textarea id="schedule-content" placeholder="Message content" rows="4" maxlength="10000"></textarea>
                </div>
                <div class="modal-footer">
                    <button class="btn-primary" id="schedule-confirm">Schedule</button>
                    <button class="btn-secondary" id="schedule-cancel">Cancel</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);

        document.getElementById('schedule-confirm').addEventListener('click', async () => {
            const recipient = document.getElementById('schedule-recipient').value;
            const datetime = document.getElementById('schedule-datetime').value;
            const content = document.getElementById('schedule-content').value;
            
            if (recipient && datetime && content) {
                await this.scheduleMessage(recipient, content, '', new Date(datetime).toISOString());
                modal.remove();
            }
        });

        document.getElementById('schedule-cancel').addEventListener('click', () => modal.remove());
        document.querySelector('.close-modal').addEventListener('click', () => modal.remove());
    }

    /**
     * Show block modal
     */
    showBlockModal() {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Block User</h3>
                    <button class="close-modal">&times;</button>
                </div>
                <div class="modal-body">
                    <input type="text" id="block-username" placeholder="Username to block" maxlength="255">
                    <textarea id="block-reason" placeholder="Reason (optional)" maxlength="255" rows="2"></textarea>
                </div>
                <div class="modal-footer">
                    <button class="btn-primary" id="block-confirm">Block</button>
                    <button class="btn-secondary" id="block-cancel">Cancel</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);

        document.getElementById('block-confirm').addEventListener('click', async () => {
            const username = document.getElementById('block-username').value;
            const reason = document.getElementById('block-reason').value;
            
            if (username) {
                await this.blockUser(username, reason);
                modal.remove();
            }
        });

        document.getElementById('block-cancel').addEventListener('click', () => modal.remove());
        document.querySelector('.close-modal').addEventListener('click', () => modal.remove());
    }

    /**
     * Show use template modal
     */
    showUseTemplateModal(templateId) {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Use Template</h3>
                    <button class="close-modal">&times;</button>
                </div>
                <div class="modal-body">
                    <input type="text" id="template-recipient" placeholder="Recipient username" maxlength="255">
                    <input type="text" id="template-subject" placeholder="Subject (optional)" maxlength="255">
                </div>
                <div class="modal-footer">
                    <button class="btn-primary" id="template-send">Send</button>
                    <button class="btn-secondary" id="template-cancel">Cancel</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);

        document.getElementById('template-send').addEventListener('click', async () => {
            const recipient = document.getElementById('template-recipient').value;
            const subject = document.getElementById('template-subject').value;
            
            if (recipient) {
                await this.useTemplate(templateId, recipient, subject);
                modal.remove();
            }
        });

        document.getElementById('template-cancel').addEventListener('click', () => modal.remove());
        document.querySelector('.close-modal').addEventListener('click', () => modal.remove());
    }

    // ============= Utility Methods =============

    /**
     * Polling for new messages
     */
    startPolling() {
        this.pollTimer = setInterval(() => {
            if (this.selectedTab === 'inbox') {
                this.loadInbox();
            } else if (this.currentConversation) {
                this.loadConversation(this.currentConversation.withUser);
            }
        }, this.pollInterval);
    }

    /**
     * Stop polling
     */
    stopPolling() {
        if (this.pollTimer) {
            clearInterval(this.pollTimer);
        }
    }

    /**
     * Delete template
     */
    async deleteTemplate(templateId) {
        if (confirm('Are you sure you want to delete this template?')) {
            try {
                const response = await fetch(`${this.apiBase}/templates/${templateId}`, {
                    method: 'DELETE',
                    headers: {
                        'X-CSRF-Token': this.csrfToken
                    }
                });

                if (!response.ok) throw new Error('Failed to delete template');

                this.showSuccess('Template deleted');
                this.loadTemplates();
            } catch (error) {
                this.showError('Failed to delete template');
            }
        }
    }

    /**
     * Use template
     */
    async useTemplate(templateId, recipient, subject) {
        try {
            const response = await fetch(`${this.apiBase}/templates/${templateId}/use`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-Token': this.csrfToken
                },
                body: JSON.stringify({
                    recipient: recipient,
                    subject: subject
                })
            });

            if (!response.ok) throw new Error('Failed to use template');

            this.showSuccess('Message sent from template!');
            this.loadInbox();
        } catch (error) {
            this.showError(error.message);
        }
    }

    /**
     * Cancel scheduled message
     */
    async cancelScheduledMessage(messageId) {
        try {
            const response = await fetch(`${this.apiBase}/scheduled/${messageId}`, {
                method: 'DELETE',
                headers: {
                    'X-CSRF-Token': this.csrfToken
                }
            });

            if (!response.ok) throw new Error('Failed to cancel');

            this.showSuccess('Scheduled message cancelled');
            this.loadScheduledMessages();
        } catch (error) {
            this.showError('Failed to cancel scheduled message');
        }
    }

    /**
     * Update unread badge
     */
    updateUnreadBadge() {
        const badge = document.getElementById('unread-badge');
        if (badge) {
            badge.textContent = this.unreadCount;
            badge.style.display = this.unreadCount > 0 ? 'block' : 'none';
        }
    }

    /**
     * Format timestamp
     */
    formatTime(timestamp) {
        if (!timestamp) return '';
        const date = new Date(timestamp);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffMins < 1) return 'just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        if (diffDays < 7) return `${diffDays}d ago`;
        
        return date.toLocaleDateString();
    }

    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Show success message
     */
    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    /**
     * Show error message
     */
    showError(message) {
        this.showNotification(message, 'error');
    }

    /**
     * Show notification
     */
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        document.body.appendChild(notification);

        setTimeout(() => {
            notification.classList.add('show');
        }, 10);

        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    /**
     * Destroy the messaging system
     */
    destroy() {
        this.stopPolling();
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MessagingSystem;
}
