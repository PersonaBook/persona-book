// chat.js
// 테스트를 위한 페이지
// `/chat?userId={사용자_ID}&bookId={책_ID}`

const userId = Number(document.getElementById('userId').value);
const bookId = Number(document.getElementById('bookId').value);


const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const loadingIndicator = document.getElementById('loadingIndicator');
const chatForm = document.getElementById('chatForm');
const debugStateEl = document.getElementById('debugState');
const errorMessage = document.getElementById('errorMessage');

let currentState = 'WAITING_USER_SELECT_FEATURE';

// --- 초기화 ---
document.addEventListener('DOMContentLoaded', async () => {
    messageInput.focus();
    await loadChatHistory();
    await checkConnection();
    if (chatMessages.children.length === 0) {
        await startNewChat(); // 초기 상태 유도
    }
});

// --- 이벤트 리스너 ---
chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const message = messageInput.value.trim();
    if (message) sendMessage(message);
});

// --- 메시지 전송 ---
async function sendMessage(messageContent) {
    const payload = {
        userId: userId,
        bookId: bookId,
        content: messageContent,
        sender: 'USER',
        messageType: 'TEXT',
        chatState: currentState
    };

    if (messageContent.trim()) {
        addMessage('user', messageContent);
    }

    messageInput.value = '';
    setSendButtonState(false);
    showLoading(true);

    try {
        const response = await fetch('/api/chat/send', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const aiResponses = await response.json(); // List 형태

        aiResponses.forEach((ai) => {
            if (ai.content?.trim()) {
                addMessage('ai', ai.content, ai.messageType, ai.options || []);
            }
        });

        // 마지막 응답의 상태로 currentState 갱신
        if (aiResponses.length > 0) {
            currentState = aiResponses[aiResponses.length - 1].chatState;
        }

        updateDebugState();
        checkConnection();
    } catch (err) {
        console.error("서버 전송 오류:", err);
        addMessage('ai', '⚠️ 서버 전송에 실패했습니다.');
    } finally {
        setSendButtonState(true);
        showLoading(false);
        messageInput.focus();
    }
}

// --- 메시지 렌더링 ---
function addMessage(sender, text, messageType = 'TEXT', options = []) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    const escapedText = text.replace(/</g, "&lt;").replace(/>/g, "&gt;");

    let contentHTML = `<div class="message-content">${escapedText}</div>`;

    if (messageType === 'SELECTION') {
        const buttonsHTML = options.map((opt, idx) =>
            `<button class="quick-btn" onclick="sendMessage('${idx + 1}')">${idx + 1}. ${opt}</button>`
        ).join('');
        contentHTML = `<div class="message-content">${escapedText}<div class="quick-actions">${buttonsHTML}</div></div>`;
    } else if (messageType === 'RATING') {
        let starsHTML = `<div class="rating-stars" onmouseout="styleStars(this, 0)">`;
        for (let i = 1; i <= 5; i++) {
            starsHTML += `<span id="star_${i}" onmouseover="styleStars(this.parentElement, ${i})" onclick="sendMessage('${i}')">☆</span>`;
        }
        starsHTML += `</div>`;
        contentHTML = `<div class="message-content">${escapedText}<br>${starsHTML}</div>`;
    }

    messageDiv.innerHTML = contentHTML;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// --- 별점 스타일 ---
function styleStars(container, rating) {
    for (let i = 1; i <= 5; i++) {
        const star = container.querySelector(`#star_${i}`);
        if (star) star.textContent = i <= rating ? '★' : '☆';
    }
}

// --- 초기 채팅 시작 ---
async function startNewChat() {
    currentState = 'WAITING_USER_SELECT_FEATURE';

    // 상태 유도를 위한 빈 메시지
    await sendMessage('');
}

// --- 채팅 이력 불러오기 ---
async function loadChatHistory() {
    showLoading(true);
    try {
        const response = await fetch(`/api/chat/history?userId=${userId}&bookId=${bookId}`);
        const history = await response.json();

        chatMessages.innerHTML = '';
        if (history?.length) {
            history.forEach(msg => {
                if (msg.content?.trim()) {
                    addMessage(msg.sender.toLowerCase(), msg.content, msg.messageType, msg.options || []);
                }
            });
            currentState = history[history.length - 1].chatState;
        }
    } catch (err) {
        console.error("이력 로딩 실패:", err);
    } finally {
        showLoading(false);
        updateDebugState();
    }
}

// --- 삭제 후 새로 시작 ---
async function deleteChatHistoryAndRestart() {
    if (!confirm('모든 대화 기록을 삭제하고 새로 시작하시겠습니까?')) return;

    showLoading(true);
    try {
        await fetch(`/api/chat/history?userId=${userId}&bookId=${bookId}`, { method: 'DELETE' });
        chatMessages.innerHTML = '';  // 화면의 기존 메시지 제거
        await startNewChat();
    } catch (err) {
        showError("이력 삭제 실패");
    } finally {
        showLoading(false);
    }
}

// --- 상태 표시 ---
function updateDebugState() {
    debugStateEl.textContent = currentState || 'N/A';
    document.getElementById('newChatButton').style.display = currentState !== 'WAITING_USER_SELECT_FEATURE' ? 'inline-block' : 'none';
}

// --- 유틸리티 ---
function showLoading(show) {
    loadingIndicator.style.display = show ? 'block' : 'none';
}

function showError(msg) {
    errorMessage.textContent = msg;
    errorMessage.style.display = 'block';
    setTimeout(() => errorMessage.style.display = 'none', 5000);
}

function setSendButtonState(enabled) {
    sendButton.disabled = !enabled;
    sendButton.textContent = enabled ? '전송' : '전송 중...';
}

function checkConnection() {
    fetch("/api/chat/ping")
        .then(res => {
            document.getElementById('connectionStatus').textContent = res.ok ? '🟢 연결됨' : '🔴 끊김';
        })
        .catch(() => {
            document.getElementById('connectionStatus').textContent = '🔴 오류';
        });
}