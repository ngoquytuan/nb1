class SpamFilterApp {
    constructor() {
        this.socket = null;
        this.currentTab = 'inbox';
        this.testMessages = {
            legitimate: [
                "Xin chào, tôi muốn hỏi về sản phẩm của công ty",
                "Cảm ơn bạn đã hỗ trợ tôi hôm qua",
                "Khi nào có meeting tiếp theo?"
            ],
            suspicious: [
                "Anh có thể chuyển khoản giúp em không? Em sẽ trả sau",
                "Link này hay lắm, bạn vào xem đi",
                "Gửi mã OTP giúp tôi, tôi đang gặp khó khăn"
            ],
            spam: [
                "CHÚC MỪNG! Bạn đã trúng giải 100 triệu VND! Click link ngay",
                "Vay tiền nhanh 24/7, không cần thế chấp! Liên hệ ngay",
                "CẢNH BÁO! Tài khoản sẽ bị khóa nếu không xác thực ngay"
            ]
        };
        
        this.init();
    }
    
    init() {
        this.initSocket();
        this.initEventListeners();
        this.loadInitialData();
    }
    
    initSocket() {
        this.socket = io();
        
        this.socket.on('connect', () => {
            this.updateConnectionStatus(true);
            this.showToast('Connected to server', 'success');
        });
        
        this.socket.on('disconnect', () => {
            this.updateConnectionStatus(false);
            this.showToast('Disconnected from server', 'error');
        });
        
        this.socket.on('message_processed', (data) => {
            this.showToast(`Message ${data.message_id} processed`, 'success');
            this.loadTabData(this.currentTab);
            this.loadStats();
        });
        
        this.socket.on('status', (data) => {
            console.log('Server status:', data);
        });
    }
    
    initEventListeners() {
        // Message form submission
        const messageForm = document.getElementById('messageForm');
        messageForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.sendMessage();
        });
        
        // Tab switching
        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', (e) => {
                const tabName = e.target.onclick.toString().match(/showTab\('(.+)'\)/)[1];
                this.showTab(tabName);
            });
        });
        
        // Auto-refresh every 10 seconds
        setInterval(() => {
            this.loadTabData(this.currentTab);
            this.loadStats();
        }, 10000);
    }
    
    updateConnectionStatus(connected) {
        const statusIndicator = document.getElementById('connectionStatus');
        const dot = statusIndicator.querySelector('.status-dot');
        const text = statusIndicator.querySelector('span:last-child');
        
        if (connected) {
            dot.className = 'status-dot online';
            text.textContent = 'Connected';
        } else {
            dot.className = 'status-dot offline';
            text.textContent = 'Disconnected';
        }
    }
    
    async sendMessage() {
        const senderInput = document.getElementById('sender');
        const messageInput = document.getElementById('message');
        const processingStatus = document.getElementById('processingStatus');
        
        const sender = senderInput.value.trim();
        const content = messageInput.value.trim();
        
        if (!sender || !content) {
            this.showToast('Please fill in all fields', 'warning');
            return;
        }
        
        // Show processing status
        processingStatus.style.display = 'flex';
        
        try {
            const response = await fetch('/api/send_message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ sender, content })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showToast(`Message sent! ID: ${data.message_id}`, 'success');
                messageInput.value = '';
                
                // Auto-refresh after 3 seconds
                setTimeout(() => {
                    this.loadTabData(this.currentTab);
                    this.loadStats();
                }, 3000);
            } else {
                this.showToast(data.error || 'Failed to send message', 'error');
            }
        } catch (error) {
            console.error('Error sending message:', error);
            this.showToast('Network error', 'error');
        } finally {
            processingStatus.style.display = 'none';
        }
    }
    
    sendTestMessage(type) {
        const messages = this.testMessages[type];
        const randomMessage = messages[Math.floor(Math.random() * messages.length)];
        
        document.getElementById('sender').value = `Test User (${type})`;
        document.getElementById('message').value = randomMessage;
        
        this.sendMessage();
    }
    
    showTab(tabName) {
        // Update active tab button
        document.querySelectorAll('.tab-button').forEach(button => {
            button.classList.remove('active');
        });
        event.target.classList.add('active');
        
        // Update active tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}-tab`).classList.add('active');
        
        this.currentTab = tabName;
        this.loadTabData(tabName);
    }
    
    async loadTabData(tabName) {
        let apiEndpoint;
        let containerId;
        
        switch (tabName) {
            case 'inbox':
                apiEndpoint = '/api/inbox?status=approved';
                containerId = 'inboxMessages';
                break;
            case 'flagged':
                apiEndpoint = '/api/inbox?status=flagged';
                containerId = 'flaggedMessages';
                break;
            case 'blocked':
                apiEndpoint = '/api/inbox?status=blocked';
                containerId = 'blockedMessages';
                break;
            case 'admin':
                apiEndpoint = '/api/admin/messages';
                containerId = 'adminMessages';
                break;
            default:
                return;
        }
        
        try {
            const response = await fetch(apiEndpoint);
            const data = await response.json();
            
            this.renderMessages(data, containerId, tabName === 'admin');
        } catch (error) {
            console.error(`Error loading ${tabName} data:`, error);
            this.showToast(`Failed to load ${tabName} data`, 'error');
        }
    }
    
    renderMessages(messages, containerId, isAdmin = false) {
        const container = document.getElementById(containerId);
        
        if (!messages || messages.length === 0) {
            container.innerHTML = '<p class="empty-state">No messages found...</p>';
            return;
        }
        
        const messagesHtml = messages.map(message => {
            const createdAt = new Date(message.created_at);
            const timeStr = createdAt.toLocaleString();
            
            let classificationBadge = '';
            if (message.classification) {
                classificationBadge = `
                    <span class="classification-badge ${message.classification}">
                        ${message.classification.toUpperCase()}
                    </span>
                `;
            }
            
            let scores = '';
            if (message.naive_bayes_score !== null) {
                scores += `NB: ${(message.naive_bayes_score * 100).toFixed(1)}%`;
            }
            if (message.llm_score !== null) {
                if (scores) scores += ' | ';
                scores += `LLM: ${(message.llm_score * 100).toFixed(1)}%`;
            }
            
            let adminInfo = '';
            if (isAdmin && message.filter_history) {
                adminInfo = `
                    <div class="filter-history">
                        <strong>Filter History:</strong><br>
                        ${message.filter_history.replace(/\|/g, '<br>')}
                    </div>
                `;
            }
            
            return `
                <div class="message-item ${message.classification || ''}">
                    <div class="message-header">
                        <span class="message-sender">${this.escapeHtml(message.sender)}</span>
                        <span class="message-time">${timeStr}</span>
                    </div>
                    <div class="message-content">
                        ${this.escapeHtml(message.content)}
                    </div>
                    <div class="message-meta">
                        <span>ID: ${message.id}</span>
                        <span>Status: ${message.status}</span>
                        ${classificationBadge}
                        ${scores ? `<span>Scores: ${scores}</span>` : ''}
                    </div>
                    ${adminInfo}
                </div>
            `;
        }).join('');
        
        container.innerHTML = messagesHtml;
    }
    
    async loadStats() {
        try {
            const response = await fetch('/api/stats');
            const stats = await response.json();
            
            document.getElementById('totalProcessed').textContent = stats.total_processed || '0';
            document.getElementById('legitimateCount').textContent = stats.legitimate || '0';
            document.getElementById('suspiciousCount').textContent = stats.suspicious || '0';
            document.getElementById('blockedCount').textContent = stats.blocked || '0';
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }
    
    loadInitialData() {
        this.loadTabData('inbox');
        this.loadStats();
    }
    
    refreshAllData() {
        this.loadTabData(this.currentTab);
        this.loadStats();
        this.showToast('Data refreshed', 'success');
    }
    
    exportLogs() {
        // Simple CSV export functionality
        fetch('/api/admin/messages')
            .then(response => response.json())
            .then(data => {
                const csv = this.convertToCSV(data);
                this.downloadCSV(csv, 'spam_filter_logs.csv');
                this.showToast('Logs exported', 'success');
            })
            .catch(error => {
                console.error('Export error:', error);
                this.showToast('Export failed', 'error');
            });
    }
    
    convertToCSV(data) {
        const headers = ['ID', 'Content', 'Sender', 'Status', 'Classification', 'NB Score', 'LLM Score', 'Created At', 'Filter History'];
        
        const rows = data.map(item => [
            item.id,
            `"${(item.content || '').replace(/"/g, '""')}"`,
            `"${(item.sender || '').replace(/"/g, '""')}"`,
            item.status || '',
            item.classification || '',
            item.naive_bayes_score || '',
            item.llm_score || '',
            item.created_at || '',
            `"${(item.filter_history || '').replace(/"/g, '""')}"`
        ]);
        
        return [headers.join(','), ...rows.map(row => row.join(','))].join('\n');
    }
    
    downloadCSV(csv, filename) {
        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        if (link.download !== undefined) {
            const url = URL.createObjectURL(blob);
            link.setAttribute('href', url);
            link.setAttribute('download', filename);
            link.style.visibility = 'hidden';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    }
    
    showToast(message, type = 'info') {
        const toastContainer = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icon = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        }[type] || 'ℹ️';
        
        toast.innerHTML = `
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 16px;">${icon}</span>
                <span>${this.escapeHtml(message)}</span>
            </div>
        `;
        
        toastContainer.appendChild(toast);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.style.animation = 'slideOutRight 0.3s ease-in forwards';
                setTimeout(() => {
                    if (toast.parentNode) {
                        toastContainer.removeChild(toast);
                    }
                }, 300);
            }
        }, 5000);
    }
    
    escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    }
}

// Global functions for HTML onclick handlers
function showTab(tabName) {
    app.showTab(tabName);
}

function sendTestMessage(type) {
    app.sendTestMessage(type);
}

function refreshAllData() {
    app.refreshAllData();
}

function exportLogs() {
    app.exportLogs();
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new SpamFilterApp();
});

// Add slide out animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);