function toggleChatbot() {
    const chatbotWindow = document.getElementById('chatbot-window');
    chatbotWindow.style.display = chatbotWindow.style.display === 'none' ? 'block' : 'none';
}

function windowClose(id) {
    document.getElementById(id).style.display = 'none';
}

function windowMinimize(id) {
    const win = document.getElementById(id);
    win.querySelector('.card-body').style.display = 'none';
    win.querySelector('.card-footer').style.display = 'none';
}

function windowMaximize(id) {
    const win = document.getElementById(id);
    win.querySelector('.card-body').style.display = 'block';
    win.querySelector('.card-footer').style.display = 'flex';
}






const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const loadingIndicator = document.getElementById('loadingIndicator');
const chatForm = document.getElementById('chatForm');
const statusIndicator = document.getElementById('statusIndicator');
const errorMessage = document.getElementById('errorMessage');
const debugStateEl = document.getElementById('debugState');

// 현재 상태 관리
let currentFeatureContext = 'INITIAL';
let currentStageContext = 'START';
let sending = false;

// 페이지 로딩 시 동작
document.addEventListener('DOMContentLoaded', async function() {
    messageInput.focus();
    await loadChatHistory();
    await checkConnection();
    // 기존 이력이 없을 경우 자동으로 초기 메시지 전송
    if (chatMessages.children.length === 0) await startNewChat();
});

// 채팅 제출
chatForm.addEventListener('submit', function(e) {
    e.preventDefault();
    const message = messageInput.value.trim();
    if (message) sendMessage(message);
});

function updateDebugState() {
    debugStateEl.textContent = `${currentFeatureContext} / ${currentStageContext}`;
    toggleNewChatButtonVisibility();
}

function toggleNewChatButtonVisibility() {
    const newChatBtn = document.getElementById('newChatButton');
    const isStart = currentStageContext === 'SELECT_TYPE';
    newChatBtn.style.display = isStart ? 'none' : 'inline-block';
}

function addMessage(sender, content, messageType = 'TEXT', options = []) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    const timestamp = new Date().toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' });
    let innerContent = '';

    if (messageType === 'TEXT') {
        innerContent = `<div class="message-content">${content}</div>`;
    } else if (messageType === 'SELECTION') {
        innerContent = `<div class="message-content">${content}<br>${options.map((opt, idx) => `<button class='quick-btn' onclick='sendQuickMessage("${opt}")'>${idx+1}. ${opt}</button>`).join(' ')}</div>`;
    } else if (messageType === 'RATING') {
        innerContent = `<div class="message-content">${content}<br><input type='number' min='1' max='5' placeholder='1~5점 입력' onkeypress='handleRatingInput(event)'></div>`;
    }

    messageDiv.innerHTML = `<div class="message-sender">${sender.toUpperCase()} ${timestamp}</div>${innerContent}`;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function handleRatingInput(e) {
    if (e.key === 'Enter') {
        const value = e.target.value;
        if (value) sendMessage(value);
    }
}

async function sendMessage(content) {
    const userId = document.getElementById('userId').value;
    const bookId = parseInt(document.getElementById('bookId').value);
    if (!userId || !bookId) return showError('사용자 ID와 교재 ID를 입력해주세요.');

    // ✅ 빈 문자열이면 user 메시지 렌더링 생략
    if (content.trim() !== '') {
        addMessage('user', content);
    }

    messageInput.value = '';
    setSendButtonState(false);
    showLoading(true);
    hideError();

    const userMessage = {
        userId, bookId, content, sender: 'USER', messageType: 'TEXT',
        featureContext: currentFeatureContext,
        stageContext: currentStageContext
    };

    try {
        const response = await fetch('/api/chat/send', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userMessage)
        });

        if (response.ok) {
            const aiResponse = await response.json();
            addMessage('ai', aiResponse.content, aiResponse.messageType, aiResponse.options || []);
            currentFeatureContext = aiResponse.featureContext || currentFeatureContext;
            currentStageContext = aiResponse.stageContext || currentStageContext;
            updateDebugState();
            updateConnectionStatus(true);
        } else {
            const errorMsg = (await response.json().catch(() => ({}))).message || `서버 오류 (${response.status})`;
            showError(errorMsg);
            addMessage('ai', '죄송합니다. 오류가 발생했습니다.');
            updateConnectionStatus(false);
        }
    } catch (err) {
        console.error(err);
        showError('네트워크 오류 발생');
        updateConnectionStatus(false);
    } finally {
        setSendButtonState(true);
        showLoading(false);
        messageInput.focus();
    }
}

function sendQuickMessage(content) {
    if (sending) return;
    sending = true;
    sendMessage(content).finally(() => sending = false);
}

function setSendButtonState(enabled) {
    sendButton.disabled = !enabled;
    sendButton.textContent = enabled ? '전송' : '전송 중...';
}

function showLoading(show) {
    loadingIndicator.classList.toggle('show', show);
    if (show) chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.add('show');
    setTimeout(hideError, 5000);
}

function hideError() {
    errorMessage.classList.remove('show');
}

function updateConnectionStatus(connected) {
    statusIndicator.className = connected ? 'status-indicator connected' : 'status-indicator disconnected';
    statusIndicator.textContent = connected ? '🟢 연결됨' : '🔴 연결 끊김';
}

// ✅ 채팅 이력만 삭제하는 함수
async function deleteChatHistory() {
    const userId = document.getElementById('userId').value;
    const bookId = parseInt(document.getElementById('bookId').value);
    if (!userId || !bookId) return;

    try {
        await fetch(`/api/chat/history?userId=${userId}&bookId=${bookId}`, { method: 'DELETE' });
    } catch (err) {
        console.error('채팅 이력 삭제 실패:', err);
    }
}

// ✅ 새로운 채팅 흐름을 시작 (START 상태로 전환)
async function startNewChat() {
    currentFeatureContext = 'INITIAL';
    currentStageContext = 'START';
    updateDebugState();
    messageInput.focus();
    hideError();
    await sendMessage(''); // START 상태 흐름 유도
}

// ✅ 전체 리셋 흐름 (사용자 트리거)
async function deleteChatHistoryAndRestart() {
    if (!confirm('정말로 채팅 이력을 삭제하시겠습니까? 삭제된 데이터는 복구할 수 없습니다.')) return;

    await deleteChatHistory();         // 🔸 DB에서 채팅 이력 삭제
    chatMessages.innerHTML = '';       // 🔸 화면의 기존 메시지 제거
    currentFeatureContext = 'INITIAL'; // 🔸 상태 초기화
    currentStageContext = 'START';
    updateDebugState();                // 🔸 상태 디버그 UI 갱신
    await loadChatHistory();           // 🔸 DB 기준으로 이력 로딩 (일반적으로 없음)
    await sendMessage('');             // 🔸 START 메시지 흐름 유도
}

async function loadChatHistory() {
    const userId = document.getElementById('userId').value;
    const bookId = parseInt(document.getElementById('bookId').value);
    if (!userId || !bookId) return;

    try {
        const response = await fetch(`/api/chat/history?userId=${userId}&bookId=${bookId}`);
        if (!response.ok) return;

        const history = await response.json();
        chatMessages.innerHTML = ''; // 기존 메시지 초기화

        history.forEach(msg => {
            // ✅ 빈 문자열 메시지는 렌더링 생략
            if (!msg.content || msg.content.trim() === '') return;
            addMessage(msg.sender.toLowerCase(), msg.content, msg.messageType || 'TEXT');
        });

        const last = history[history.length - 1];
        if (last) {
            currentFeatureContext = last.featureContext || 'INITIAL';
            currentStageContext = last.stageContext || 'START';
            updateDebugState();
        }
    } catch (err) {
        console.error(err);
        showError('채팅 기록을 불러오는 데 실패했습니다.');
    }
}

async function checkConnection() {
    try {
        const res = await fetch('/api/chat/ping');
        updateConnectionStatus(res.ok);
    } catch {
        updateConnectionStatus(false);
    }
}


messageInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        chatForm.dispatchEvent(new Event('submit'));
    }
});

setInterval(checkConnection, 30000);