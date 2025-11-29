// Library Chat with Session History
class LibraryChat {
    constructor() {
        this.currentSessionId = null;
        this.sessions = new Map(); // sessionId -> {messages[], createdAt, preview}
        this.apiBase = 'http://localhost:8000';
        this.initializeEventListeners();
        this.loadSessions();
    }

    initializeEventListeners() {
        // Send message
        document.getElementById('sendBtn').addEventListener('click', () => this.sendMessage());
        document.getElementById('messageInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });

        // New chat button
        document.getElementById('newChatBtn').addEventListener('click', () => this.createNewSession());
    }

    createNewSession() {
        this.currentSessionId = null;
        this.clearChat();
        this.updateSessionInfo();
        this.addMessage('assistant', 'Started a new chat session. How can I help you with library operations today?');
        this.updateChatHistory();
    }

    async sendMessage() {
        const input = document.getElementById('messageInput');
        const message = input.value.trim();

        if (!message) return;

        input.value = '';
        this.addMessage('user', message);
        this.showLoading(true);

        try {
            const response = await fetch(`${this.apiBase}/chat`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    message: message,
                    session_id: this.currentSessionId
                })
            });

            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

            const data = await response.json();

            // Update session
            if (!this.currentSessionId) {
                this.currentSessionId = data.session_id;
                this.sessions.set(this.currentSessionId, {
                    messages: [],
                    createdAt: new Date(),
                    preview: message.substring(0, 50) + (message.length > 50 ? '...' : '')
                });
            }

            // Add assistant response
            this.addMessage('assistant', data.response, data.tools_used);

            // Update session data
            const session = this.sessions.get(this.currentSessionId);
            if (session) {
                session.messages.push({role: 'user', content: message});
                session.messages.push({role: 'assistant', content: data.response});
                session.preview = message.substring(0, 50) + (message.length > 50 ? '...' : '');
            }

            this.updateChatHistory();
            this.saveSessions();

        } catch (error) {
            console.error('Error:', error);
            this.addMessage('assistant', 'Sorry, I encountered an error. Please try again.');
        } finally {
            this.showLoading(false);
        }
    }

    addMessage(role, content, toolsUsed = []) {
        const messagesContainer = document.getElementById('messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.innerHTML = content.replace(/\n/g, '<br>');
        
        messageDiv.appendChild(messageContent);
        
        // Add tool usage
        if (toolsUsed && toolsUsed.length > 0 && role === 'assistant') {
            const toolUsageDiv = document.createElement('div');
            toolUsageDiv.className = 'tool-usage';
            toolUsageDiv.textContent = toolsUsed.length === 1 ? 
                `Used tool: ${toolsUsed[0]}` : 
                `Used tools: ${toolsUsed.join(', ')}`;
            messageDiv.appendChild(toolUsageDiv);
        }
        
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    updateChatHistory() {
        const historyContainer = document.getElementById('chatHistory');
        historyContainer.innerHTML = '';

        this.sessions.forEach((session, sessionId) => {
            const sessionDiv = document.createElement('div');
            sessionDiv.className = `chat-session ${sessionId === this.currentSessionId ? 'active' : ''}`;
            sessionDiv.addEventListener('click', () => this.loadSession(sessionId));

            const previewDiv = document.createElement('div');
            previewDiv.className = 'session-preview';
            previewDiv.textContent = session.preview || 'New chat';

            const dateDiv = document.createElement('div');
            dateDiv.className = 'session-date';
            dateDiv.textContent = this.formatDate(session.createdAt);

            sessionDiv.appendChild(previewDiv);
            sessionDiv.appendChild(dateDiv);
            historyContainer.appendChild(sessionDiv);
        });

        // Add "New Session" at top if no active session
        if (!this.currentSessionId) {
            const newSessionDiv = document.createElement('div');
            newSessionDiv.className = 'chat-session active';
            newSessionDiv.innerHTML = `
                <div class="session-preview">New Session</div>
                <div class="session-date">Just now</div>
            `;
            historyContainer.insertBefore(newSessionDiv, historyContainer.firstChild);
        }
    }

    loadSession(sessionId) {
        this.currentSessionId = sessionId;
        this.clearChat();
        
        const session = this.sessions.get(sessionId);
        if (session && session.messages) {
            session.messages.forEach(msg => {
                this.addMessage(msg.role, msg.content);
            });
        }
        
        this.updateSessionInfo();
        this.updateChatHistory();
    }

    clearChat() {
        const messagesContainer = document.getElementById('messages');
        messagesContainer.innerHTML = '';
        
        // Add welcome message for new sessions
        if (!this.currentSessionId) {
            const welcomeMsg = document.createElement('div');
            welcomeMsg.className = 'message welcome-message';
            welcomeMsg.innerHTML = `
                <div class="message-content">
                    <strong>Assistant:</strong> Hello! I'm your Library Desk Agent. I can help you find books, create orders, check inventory, and more.
                </div>
            `;
            messagesContainer.appendChild(welcomeMsg);
        }
    }

    updateSessionInfo() {
        const sessionElement = document.getElementById('sessionStatus');
        if (this.currentSessionId) {
            sessionElement.textContent = `Session: ${this.currentSessionId.substring(0, 8)}...`;
        } else {
            sessionElement.textContent = 'New Session';
        }
    }

    showLoading(show) {
        const loading = document.getElementById('loading');
        const sendBtn = document.getElementById('sendBtn');
        
        if (show) {
            loading.classList.remove('hidden');
            sendBtn.disabled = true;
            sendBtn.textContent = 'Sending...';
        } else {
            loading.classList.add('hidden');
            sendBtn.disabled = false;
            sendBtn.textContent = 'Send';
        }
    }

    formatDate(date) {
        const now = new Date();
        const diff = now - date;
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(diff / 3600000);
        const days = Math.floor(diff / 86400000);

        if (minutes < 1) return 'Just now';
        if (minutes < 60) return `${minutes}m ago`;
        if (hours < 24) return `${hours}h ago`;
        return `${days}d ago`;
    }

    saveSessions() {
        const sessionsData = Object.fromEntries(this.sessions);
        localStorage.setItem('library_chat_sessions', JSON.stringify(sessionsData));
    }

    loadSessions() {
        const saved = localStorage.getItem('library_chat_sessions');
        if (saved) {
            const sessionsData = JSON.parse(saved);
            Object.entries(sessionsData).forEach(([sessionId, session]) => {
                this.sessions.set(sessionId, {
                    ...session,
                    createdAt: new Date(session.createdAt)
                });
            });
            this.updateChatHistory();
        }
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    new LibraryChat();
});