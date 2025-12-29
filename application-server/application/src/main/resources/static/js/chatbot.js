(function() {
    // 이 함수는 외부에서 호출되어 채팅 기능을 초기화합니다.
    // renderChatWindow 함수에 의해 호출되며, userId와 bookId는 이미 hidden input으로 삽입되어 있습니다.
    window.initializeChatFunctionality = function() {
        const chatForm = document.getElementById('chatForm');
        const messageInput = document.getElementById('messageInput');
        const chatMessages = document.getElementById('chatMessages');
        const loadingIndicator = document.getElementById('loadingIndicator');
        const debugStateEl = document.getElementById('debugState');
        const newChatButton = document.getElementById('newChatButton');
        const deleteHistoryBtn = document.getElementById('deleteHistoryBtn');
        const sendButton = document.getElementById('sendButton');

        const userId = document.getElementById('userId').value;
        const bookId = document.getElementById('bookId').value;

        let currentState = 'WAITING_USER_SELECT_FEATURE';
        let initialMessageSent = false; // 새 채팅 시작 시 중복 메시지 방지

        // --- Event Listeners ---
        chatForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const message = messageInput.value.trim();
            if (message) {
                sendMessage(message);
            }
        });

        newChatButton.addEventListener('click', () => {
            chatMessages.innerHTML = '';
            initialMessageSent = false;
            startNewChat();
        });

        deleteHistoryBtn.addEventListener('click', () => deleteChatHistoryAndRestart());

        // --- Core Functions ---
        function sendMessage(messageContent) {
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

            sendChatMessage(payload)
                .then(aiResponses => { // apiCall에서 data를 바로 반환하므로 aiResponses.data 제거
                    aiResponses.forEach(ai => {
                        if (ai.content?.trim()) {
                            addMessage('ai', ai.content, ai.messageType, ai.options || []);
                        }
                    });
                    if (aiResponses.length > 0) {
                        currentState = aiResponses[aiResponses.length - 1].chatState;
                    }
                    updateDebugState();
                })
                .catch(err => {
                    console.error("서버 전송 오류:", err);
                    addMessage('ai', '⚠️ 서버 전송에 실패했습니다.');
                    // handleApiError는 api.js에서 처리되므로 여기서는 추가 호출하지 않습니다.
                })
                .finally(() => {
                    setSendButtonState(true);
                    showLoading(false);
                    messageInput.focus();
                });
        }

        function addMessage(sender, text, messageType = 'TEXT', options = []) {
            const escapedText = text.replace(/</g, "&lt;").replace(/>/g, "&gt;");
            let contentHTML = `<div class="message-content">${escapedText}</div>`;

            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}`;

            if (messageType === 'SELECTION') {
                const buttonsHTML = options.map((opt, idx) =>
                    `<button class="quick-btn" data-value="${idx + 1}">${idx + 1}. ${opt}</button>`
                ).join('');
                contentHTML = `<div class="message-content">${escapedText}<div class="quick-actions">${buttonsHTML}</div></div>`;
            } else if (messageType === 'RATING') {
                let starsHTML = `<div class="rating-stars">`;
                for (let i = 1; i <= 5; i++) {
                    starsHTML += `<span class="star-icon" data-value="${i}">☆</span>`;
                }
                starsHTML += `</div>`;
                contentHTML = `<div class="message-content">${escapedText}<br>${starsHTML}</div>`;
            }

            messageDiv.innerHTML = contentHTML;
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;

            // 동적으로 추가된 요소에 이벤트 리스너 바인딩
            if (messageType === 'SELECTION') {
                messageDiv.querySelectorAll('.quick-btn').forEach(button => {
                    button.addEventListener('click', () => sendMessage(button.dataset.value));
                });
            } else if (messageType === 'RATING') {
                messageDiv.querySelectorAll('.star-icon').forEach(star => {
                    star.addEventListener('click', () => sendMessage(star.dataset.value));
                    star.addEventListener('mouseover', () => styleStars(star.parentElement, parseInt(star.dataset.value)));
                });
                const ratingStarsContainer = messageDiv.querySelector('.rating-stars');
                if (ratingStarsContainer) {
                    ratingStarsContainer.addEventListener('mouseout', () => styleStars(ratingStarsContainer, 0));
                }
            }
        }

        // --- 별점 스타일 ---
        function styleStars(container, rating) {
            for (let i = 1; i <= 5; i++) {
                const star = container.querySelector(`[data-value="${i}"]`);
                if (star) star.textContent = i <= rating ? '★' : '☆';
            }
        }

        function loadChatHistory() {
            showLoading(true);
            getChatHistory(userId, bookId)
                .then(history => {
                    chatMessages.innerHTML = '';
                    if (history?.length) {
                        history.forEach(msg => {
                            if (msg.content?.trim()) {
                                addMessage(msg.sender.toLowerCase(), msg.content, msg.messageType, msg.options || []);
                            }
                        });
                        currentState = history[history.length - 1].chatState;
                    }
                })
                .catch(err => {
                    console.error("이력 로딩 실패:", err);
                })
                .finally(() => {
                    showLoading(false);
                    updateDebugState();
                    if (chatMessages.children.length === 0) {
                        startNewChat();
                    }
                });
        }

        function startNewChat() {
            if (initialMessageSent) return;
            initialMessageSent = true;

            currentState = 'WAITING_USER_SELECT_FEATURE';
            sendMessage('');
        }

        function deleteChatHistoryAndRestart() {
            if (!confirm('모든 대화 기록을 삭제하고 새로 시작하시겠습니까?')) return;

            initialMessageSent = false;

            showLoading(true);
            deleteChatHistory(userId, bookId)
                .then(() => {
                    chatMessages.innerHTML = '';
                    startNewChat();
                })
                .catch(err => {
                    showError("이력 삭제 실패");
                })
                .finally(() => {
                    showLoading(false);
                });
        }

        function updateDebugState() {
            debugStateEl.textContent = currentState || 'N/A';
            newChatButton.style.display = currentState !== 'WAITING_USER_SELECT_FEATURE' ? 'inline-block' : 'none';
        }

        function showLoading(show) {
            loadingIndicator.style.display = show ? 'block' : 'none';
        }

        function showError(msg) {
            const errorMessageEl = document.getElementById('errorMessage');
            if (errorMessageEl) {
                errorMessageEl.textContent = msg;
                errorMessageEl.style.display = 'block';
                setTimeout(() => errorMessageEl.style.display = 'none', 5000);
            }
        }

        function setSendButtonState(enabled) {
            sendButton.disabled = !enabled;
            sendButton.textContent = enabled ? '전송' : '전송 중...';
        }

        // Initial Load (initializeChatFunctionality가 호출될 때 한번 로드)
        loadChatHistory();
    };

    // DOMContentLoaded 이벤트는 chatbot.js가 로드될 때 단 한 번만 발생합니다.
    // 이 부분은 chat_btn 클릭 시 동적으로 chat_area를 렌더링하는 로직입니다.
    document.addEventListener('DOMContentLoaded', function() {
        const chatBtn = document.querySelector('.chat_btn > button');
        const chatArea = document.querySelector('.chat_area');

        if (!chatBtn) return;

        chatBtn.addEventListener('click', function() {
            chatArea.classList.toggle('on');

            if (chatArea.classList.contains('on')) {
                const userId = this.dataset.userId;
                const bookId = this.dataset.bookId;
                renderChatWindow(chatArea, userId, bookId);
            } else {
                // 채팅창 닫을 때 내부 HTML 비우기
                chatArea.innerHTML = '';
                chatArea.classList.remove("small", "big"); // 크기 클래스 초기화
            }
        });
    });

    // 외부에서 호출되는 렌더링 함수
    window.renderChatWindow = function(container, userId, bookId) {
        const chatHtml = `
            <div class="chat-container">
                <div class="chat-header">
                    chat
                    <div class="d-flex align-items-center">
                        <button type="button" class="chat_window_toggle">
                            <svg xmlns="http://www.w3.org/2000/svg" height="20px" viewBox="0 0 24 24" width="20px"><path d="M0 0h24v24H0V0z" fill="none"/><path d="M3 3h18v18H3V3zm2 2v14h14V5H5z"/></svg>
                        </button>
                        <button type="button" class="chat_close_btn">
                            <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 0 24 24" width="24px"><path d="M0 0h24v24H0V0z" fill="none"/><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12 19 6.41z"/></svg>
                        </button>
                    </div>
                </div>
                <div class="chat-settings d-flex">
                    <button type="button" id="deleteHistoryBtn" class="quick-btn btn btn-light rounded-0 w-50">채팅 이력 삭제</button>
                    <button type="button" id="newChatButton" class="quick-btn btn btn-light rounded-0 w-50">새로운 대화</button>
                    <input type="hidden" id="userId" value="${userId}" />
                    <input type="hidden" id="bookId" value="${bookId}" />
                </div>
                <div style="display: none">
                    상태: <span id="debugState">INITIAL / START</span>
                </div>
                <div class="chat-messages" id="chatMessages"></div>
                <div class="error-message" id="errorMessage"></div>
                <div class="loading" id="loadingIndicator">AI가 응답을 생성하고 있습니다...</div>
                <div class="chat-input-container">
                    <form class="chat-input-form" id="chatForm">
                        <input type="text" class="chat-input" id="messageInput" placeholder="메시지를 입력하세요..." />
                        <button type="submit" class="send-button" id="sendButton">전송</button>
                    </form>
                </div>
            </div>`;

        container.innerHTML = chatHtml;

        // 새로 생성된 DOM 요소에 이벤트 리스너 바인딩
        const chatWindowToggle = container.querySelector('.chat_window_toggle');
        const chatCloseBtn = container.querySelector('.chat_close_btn');
        const chatAreaEl = document.querySelector('.chat_area'); // .chat_area는 container의 부모일 수 있습니다.

        if (chatWindowToggle) {
            chatWindowToggle.addEventListener('click', function() {
                if (chatAreaEl.classList.contains("small")) {
                    chatAreaEl.classList.remove("small");
                    chatAreaEl.classList.add("big");
                } else {
                    chatAreaEl.classList.remove("big");
                    chatAreaEl.classList.add("small");
                }
            });
        }

        if (chatCloseBtn) {
            chatCloseBtn.addEventListener('click', () => {
                chatAreaEl.classList.remove('on');
                chatAreaEl.innerHTML = ''; // innerHTML 대신 empty()와 유사한 동작
                chatAreaEl.classList.remove("small", "big"); // 크기 클래스 초기화
            });
        }

        initializeChatFunctionality(); // userId, bookId는 initializeChatFunctionality 내부에서 DOM에서 가져옴
    };
})();