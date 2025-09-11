// Configuration
const sessionId = "{{ session_id }}"; // These will be rendered by Django
const chatTitle = "{{ chat_title }}";   // These will be rendered by Django
const csrfToken = "{{ csrf_token }}"; // These will be rendered by Django
let currentSessionId = sessionId;

// DOM Elements
const chatBox = document.getElementById('chatBox');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const newChatBtn = document.getElementById('newChatBtn');
const historyBtn = document.getElementById('historyBtn');
const historySidebar = document.getElementById('history-sidebar');
const closeSidebarBtn = document.getElementById('close-sidebar');
const sidebarOverlay = document.getElementById('sidebar-overlay');
const historyList = document.getElementById('history-list');

// Utility Functions
function scrollToBottom(smooth = true) {
    chatBox.scrollTo({
        top: chatBox.scrollHeight,
        behavior: smooth ? 'smooth' : 'auto'
    });
}

function showTypingIndicator() {
    const typingIndicator = document.createElement('div');
    typingIndicator.className = 'chat__item active typing-indicator';
    typingIndicator.innerHTML = `
        <div class="chat__box bot__chat">
            <div class="author"><span>AI Assistant</span></div>
            <div class="chat">
                <div class="typing">
                    <i class="bi bi-dot"></i>
                    <i class="bi bi-dot"></i>
                    <i class="bi bi-dot"></i>
                </div>
            </div>
        </div>
    `;
    chatBox.appendChild(typingIndicator);
    scrollToBottom();
    return typingIndicator;
}

function removeTypingIndicator(indicator) {
    if (indicator && indicator.parentNode) {
        indicator.parentNode.removeChild(indicator);
    }
}

function appendMessage(type, author, message) {
    const chatItem = document.createElement('div');
    chatItem.className = 'chat__item active';
    chatItem.innerHTML = `
        <div class="chat__box ${type}">
            <div class="author"><span>${author}</span></div>
            <div class="chat"><p>${message}</p></div>
        </div>
    `;
    chatBox.appendChild(chatItem);
    scrollToBottom();
}

function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// History Sidebar Functions
function toggleHistorySidebar() {
    const isOpen = historySidebar.classList.toggle('open');
    sidebarOverlay.classList.toggle('active', isOpen);
    historySidebar.setAttribute('aria-hidden', !isOpen);

    if (isOpen) {
        loadSessions();
    }
}

function loadSessions() {
    console.log('Fetching chat history from:', "/rag/chat/history/"); // Ensure this URL is correct
    fetch("/rag/chat/history/") // Use the correct URL for chat_history
        .then(res => {
            if (!res.ok) {
                throw new Error(`HTTP error! Status: ${res.status}`);
            }
            return res.json();
        })
        .then(data => {
            if (data.status === 'success') {
                renderSessions(data.sessions);
            } else {
                console.error('Error loading sessions:', data.message);
                historyList.innerHTML = '<div class="text-center py-3 text-muted">Failed to load chat history</div>';
            }
        })
        .catch(error => {
            console.error('Error loading sessions:', error);
            historyList.innerHTML = '<div class="text-center py-3 text-muted">Failed to load chat history</div>';
        });
}

function renderSessions(sessions) {
    historyList.innerHTML = '';

    if (!sessions || sessions.length === 0) {
        historyList.innerHTML = '<div class="text-center py-3 text-muted">No chat history yet</div>';
        return;
    }

    sessions.forEach(session => {
        const sessionElement = document.createElement('div');
        sessionElement.className = `session-item ${session.chat_session_id === currentSessionId ? 'active' : ''}`;
        sessionElement.innerHTML = `
            <div class="session-content">
                <span class="session-title">${session.chat_title || 'Untitled Chat'}</span>
                <div class="session-date">${formatDate(session.created_at)}</div>
                <div class="session-actions">
                    <button class="btn-rename" title="Rename">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn-delete" title="Delete">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </div>
        `;

        // Click handler for loading session
        sessionElement.querySelector('.session-content').addEventListener('click', (e) => {
            if (!e.target.closest('.session-actions')) {
                loadChatHistory(session.chat_session_id);
                toggleHistorySidebar();
            }
        });

        // Rename button handler
        sessionElement.querySelector('.btn-rename').addEventListener('click', (e) => {
            e.stopPropagation();
            renameSession(session.chat_session_id, sessionElement.querySelector('.session-title'));
        });

        // Delete button handler
        sessionElement.querySelector('.btn-delete').addEventListener('click', (e) => {
            e.stopPropagation();
            deleteSession(session.chat_session_id);
        });

        historyList.appendChild(sessionElement);
    });
}

function renameSession(sessionId, titleElement) {
    const currentTitle = titleElement.textContent;

    const overlay = document.createElement('div');
    overlay.className = 'rename-dialog-overlay';

    const dialog = document.createElement('div');
    dialog.className = 'rename-dialog';
    dialog.innerHTML = `
        <h3>Rename Chat</h3>
        <input type="text" value="${currentTitle}" placeholder="Enter new chat title">
        <div class="dialog-buttons">
            <button class="cancel-btn">Cancel</button>
            <button class="confirm-btn">Confirm</button>
        </div>
    `;

    document.body.appendChild(overlay);
    document.body.appendChild(dialog);

      // Show modal
        setTimeout(() => {
            overlay.classList.add('active');
            dialog.classList.add('open');
        }, 10);

        // ... (previous chat.js content)

    // Get input and buttons
    const input = dialog.querySelector('input');
    const confirmBtn = dialog.querySelector('.confirm-btn');
    const cancelBtn = dialog.querySelector('.cancel-btn');

    // Close modal function
    const closeModal = () => {
        overlay.classList.remove('active');
        dialog.classList.remove('open');
        setTimeout(() => {
            overlay.remove();
            dialog.remove();
        }, 300); // Match CSS transition duration
    };

    // Confirm button handler
    confirmBtn.addEventListener('click', () => {
        const newTitle = input.value.trim();
        if (newTitle && newTitle !== currentTitle) {
            console.log(`Renaming session ${sessionId} to: ${newTitle}`);
            fetch(`/rag/chat/rename-session/${sessionId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ title: newTitle })
            })
            .then(res => {
                if (!res.ok) {
                    throw new Error(`HTTP error! Status: ${res.status}`);
                }
                return res.json();
            })
            .then(data => {
                if (data.status === 'success') {
                    titleElement.textContent = newTitle;
                    if (sessionId === currentSessionId) {
                        newChatBtn.textContent = newTitle;
                    }
                } else {
                    console.error('Error renaming session:', data.message);
                    alert('Failed to rename session: ' + data.message);
                }
                closeModal();
            })
            .catch(error => {
                console.error('Error renaming session:', error);
                alert('Failed to rename session');
                closeModal();
            });
        } else {
            closeModal();
        }
    });

    // Cancel button handler
    cancelBtn.addEventListener('click', closeModal);

    // Overlay click handler
    overlay.addEventListener('click', closeModal);

    // Handle Enter key
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            confirmBtn.click();
        }
    });

    // Focus input
    input.focus();
}

function deleteSession(sessionId) {
    const overlay = document.createElement('div');
    overlay.className = 'delete-dialog-overlay';

    const dialog = document.createElement('div');
    dialog.className = 'delete-dialog';
    dialog.innerHTML = `
        <h3>Delete Chat</h3>
        <p>Are you sure you want to delete this chat? This action cannot be undone.</p>
        <div class="dialog-buttons">
            <button class="cancel-btn">Cancel</button>
            <button class="confirm-btn">Delete</button>
        </div>
    `;

    document.body.appendChild(overlay);
    document.body.appendChild(dialog);

    setTimeout(() => {
        overlay.classList.add('active');
        dialog.classList.add('open');
    }, 10);

    const confirmBtn = dialog.querySelector('.confirm-btn');
    const cancelBtn = dialog.querySelector('.cancel-btn');

    const closeModal = () => {
        overlay.classList.remove('active');
        dialog.classList.remove('open');
        setTimeout(() => {
            overlay.remove();
            dialog.remove();
        }, 300);
    };

    confirmBtn.addEventListener('click', () => {
        console.log(`Deleting session: ${sessionId}`);
        fetch(`/rag/chat/delete-session/${sessionId}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': csrfToken
            }
        })
        .then(res => {
            if (!res.ok) {
                throw new Error(`HTTP error! Status: ${res.status}`);
            }
            return res.json();
        })
        .then(data => {
            if (data.status === 'success') {
                if (sessionId === currentSessionId) {
                    chatBox.innerHTML = '';
                    currentSessionId = null;
                    newChatBtn.textContent = 'New Chat';
                }
                loadSessions();
            } else {
                console.error('Error deleting session:', data.message);
                alert('Failed to delete session: ' + data.message);
            }
            closeModal();
        })
        .catch(error => {
            console.error('Error deleting session:', error);
            alert('Failed to delete session');
            closeModal();
        });
    });

    cancelBtn.addEventListener('click', closeModal);
    overlay.addEventListener('click', closeModal);
}


function loadChatHistory(sessionId) {
    if (!sessionId) {
        console.error('No session ID provided, starting new session');
        startNewSession();
        return;
    }

    console.log(`Loading chat history for session: ${sessionId}`);
    fetch(`/rag/chat/history/${sessionId}/`)
        .then(res => {
            if (!res.ok) {
                return res.text().then(text => {
                    console.error('Response text:', text);
                    throw new Error(`HTTP error! Status: ${res.status}`);
                });
            }
            return res.json();
        })
        .then(data => {
            if (data.status === 'success') {
                currentSessionId = sessionId;
                chatBox.innerHTML = '';

                if (data.chat_title) {
                    newChatBtn.textContent = data.chat_title;
                }

                if (data.chats && data.chats.length > 0) {
                    data.chats.forEach(chat => {
                        appendMessage('your__chat', 'You', chat.user_message);
                        appendMessage('bot__chat', 'AI Assistant', chat.bot_response);
                    });
                } else {
                    // Optionally display a message for empty chats
                }

                scrollToBottom(false);
            } else {
                console.error('Error in response:', data.message);
                chatBox.innerHTML = '<div class="text-center py-3 text-muted">Failed to load chat history</div>';
                startNewSession(); // Fallback to new session
            }
        })
        .catch(error => {
            console.error('Error loading chat history:', error);
            chatBox.innerHTML = '<div class="text-center py-3 text-muted">Failed to load chat history</div>';
            startNewSession(); // Fallback to new session
        });
}

function startNewSession() {
    if (!csrfToken) {
        console.error('csrfToken is undefined');
        alert('Error: CSRF token not found');
        return;
    }

    console.log('Starting new session');
    fetch('/rag/chat/new-session/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        }
    })
    .then(res => {
        console.log('Fetch response status:', res.status);
        if (!res.ok) {
            throw new Error(`HTTP error! Status: ${res.status}`);
        }
        return res.json();
    })
    .then(data => {
        console.log('Fetch response data:', data);
        if (data.status === 'success') {
            currentSessionId = data.session_id;
            newChatBtn.textContent = data.chat_title;
            chatBox.innerHTML = '';
            loadSessions();
            console.log(`New session created: ${data.session_id}`);
        } else {
            console.error('Error creating session:', data.message);
            alert('Failed to create new session: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error creating new session:', error);
        alert('Failed to create new session: ' + error.message);
    });
}
// Event Listeners
sendBtn.addEventListener('click', async () => {
    const message = userInput.value.trim();
    if (!message) return;
    if (!currentSessionId) {
        await startNewSession();
    }

    userInput.disabled = true;
    sendBtn.disabled = true;

    appendMessage('your__chat', 'You', message);
    userInput.value = '';

    const typingIndicator = showTypingIndicator();

    try {
        console.log(`Sending message for session: ${currentSessionId}`);
        const response = await fetch("/rag/chat/api/", { // Use the correct URL for chat_api
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                message,
                session_id: currentSessionId,
                chat_title: newChatBtn.textContent
            })
        });

        const data = await response.json();
        removeTypingIndicator(typingIndicator);

        if (data.status === 'success') {
            appendMessage('bot__chat', 'AI Assistant', data.response);
        } else {
            console.error('Error sending message:', data.message);
            appendMessage('bot__chat', 'AI Assistant', 'Error: Failed to get response');
        }
    } catch (error) {
        console.error('Error sending message:', error);
        removeTypingIndicator(typingIndicator);
        appendMessage('bot__chat', 'AI Assistant', 'Error: Failed to get response');
    } finally {
        userInput.disabled = false;
        sendBtn.disabled = false;
        userInput.focus();
    }
});

newChatBtn.addEventListener('click', (e) => {
    e.preventDefault();
    console.log('New Chat button clicked, chatBox children:', chatBox.children.length);

    if (!chatBox) {
        console.error('chatBox is undefined');
        alert('Error: Chat box not found');
        return;
    }

    if (chatBox.children.length > 0) {
        console.log('Showing new session modal');
        const overlay = document.createElement('div');
        overlay.className = 'new-session-dialog-overlay';

        const dialog = document.createElement('div');
        dialog.className = 'new-session-dialog';
        dialog.innerHTML = `
            <h3>New Chat</h3>
            <p>Start a new chat? Your current chat will be saved.</p>
            <div class="dialog-buttons">
                <button class="cancel-btn">Cancel</button>
                <button class="confirm-btn">Start New Chat</button>
            </div>
        `;

        document.body.appendChild(overlay);
        document.body.appendChild(dialog);

        setTimeout(() => {
            overlay.classList.add('active');
            dialog.classList.add('open');
        }, 10);

        const confirmBtn = dialog.querySelector('.confirm-btn');
        const cancelBtn = dialog.querySelector('.cancel-btn');

        const closeModal = () => {
            console.log('Closing new session modal');
            overlay.classList.remove('active');
            dialog.classList.remove('open');
            setTimeout(() => {
                overlay.remove();
                dialog.remove();
            }, 300);
        };

        confirmBtn.addEventListener('click', () => {
            console.log('Confirming new session');
            startNewSession();
            closeModal();
        });

        cancelBtn.addEventListener('click', closeModal);
        overlay.addEventListener('click', closeModal);
    } else {
        console.log('No messages in chatBox, starting new session directly');
        startNewSession();
    }
});

historyBtn.addEventListener('click', () => {
    toggleHistorySidebar();
});

closeSidebarBtn.addEventListener('click', () => {
    toggleHistorySidebar();
});

sidebarOverlay.addEventListener('click', () => {
    toggleHistorySidebar();
});

userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendBtn.click();
    }
});

// Auto-resize textarea
userInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + 'px';
});

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log('Initial session ID:', sessionId);
    if (sessionId && sessionId !== 'None') { // Check for 'None' string as well if Django might render it
        loadChatHistory(sessionId);
    } else {
        startNewSession();
    }
    scrollToBottom(false);

    // Log all fetch requests for debugging
    const originalFetch = window.fetch;
    window.fetch = function(...args) {
        console.log('Fetch called with:', args);
        return originalFetch.apply(this, args);
    };
});