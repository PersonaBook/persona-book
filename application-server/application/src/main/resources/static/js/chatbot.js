// chatbot.js

$(function() {
    const chatBtn = $('.chat_btn > button');
    const chatArea = $('.chat_area');

    if (!chatBtn.length) return;

    chatBtn.on('click', function() {
        chatArea.toggleClass('on');

        if (chatArea.hasClass('on')) {
            const bookIdRaw = $(this).data('book-id');
            const bookId = Number(bookIdRaw);

            console.log("DEBUG: bookIdRaw =", bookIdRaw);
            console.log("DEBUG: bookId (numeric) =", bookId);

            if (isNaN(bookId) || bookId === 0) {
                alert("오류: 유효하지 않은 bookId입니다. 관리자에게 문의하세요.");
                chatArea.removeClass('on'); // Close chat area if bookId is invalid
                return;
            }
            renderChatWindow(chatArea, bookId);
        } else {
            chatArea.empty();
        }
    });
});

function renderChatWindow(container, bookId) {
    const chatHtml = `
        <div class="chat-container">
            <div class="chat-header">
                chat
                <div class="d-flex align-items-center">
                    <button type="button" class="chat_window">
                        <svg xmlns="http://www.w3.org/2000/svg" height="20px" viewBox="0 0 24 24" width="20px"><path d="M0 0h24v24H0V0z" fill="none"/><path d="M3 3h18v18H3V3zm2 2v14h14V5H5z"/></svg>
                    </button>
                    <button type="button" class="chat_close">
                        <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 0 24 24" width="24px"><path d="M0 0h24v24H0V0z" fill="none"/><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12 19 6.41z"/></svg>
                    </button>
                </div>
            </div>
            <div class="chat-settings d-flex">
                <button type="button" id="deleteHistoryBtn" class="quick-btn btn btn-light rounded-0 w-50">채팅 이력 삭제</button>
                <button type="button" id="newChatButton" class="quick-btn btn btn-light rounded-0 w-50">새로운 대화</button>
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

    container.html(chatHtml);
    initializeChatFunctionality(bookId);
}

function initializeChatFunctionality(bookId) {
    const chatForm = $('#chatForm');
    const messageInput = $('#messageInput');
    const chatMessages = $('#chatMessages');
    const loadingIndicator = $('#loadingIndicator');
    const debugStateEl = $('#debugState');
    const newChatButton = $('#newChatButton');
    const deleteHistoryBtn = $('#deleteHistoryBtn');
    const chatWindow = $('.chat_window');
    const closeButton = $('.chat_close');
    const sendButton = $('#sendButton');

    let currentState = 'WAITING_USER_SELECT_FEATURE';
    let initialMessageSent = false;

    // --- Event Listeners ---
    chatForm.on('submit', function(e) {
        e.preventDefault();
        const message = messageInput.val().trim();
        if (message) {
            sendMessage(message, bookId);
        }
    });

    newChatButton.on('click', () => {
        chatMessages.empty();
        initialMessageSent = false;
        startNewChat(bookId);
    });
    deleteHistoryBtn.on('click', () => deleteChatHistoryAndRestart(bookId));
    closeButton.on('click', () => {
        $('.chat_area').removeClass('on').empty();
    });

    chatWindow.click(function(){
        if( $(".chat_area").hasClass("small") ){
            $(".chat_area").removeClass("small");
            $(".chat_area").addClass("big");
        } else {
            $(".chat_area").removeClass("big");
            $(".chat_area").addClass("small");
        }
    });

    // --- Core Functions ---
    async function sendMessage(messageContent, currentBookId) {
        const payload = {
            bookId: currentBookId,
            content: messageContent,
            sender: 'USER',
            messageType: 'TEXT',
            chatState: currentState
        };

        if (messageContent.trim()) {
            addMessage('user', messageContent);
        }

        messageInput.val('');
        setSendButtonState(false);
        showLoading(true);

        try {
            const aiResponses = await apiCall('/api/chat/send', 'POST', payload);
            aiResponses.forEach(ai => {
                if (ai.content?.trim()) {
                    addMessage('ai', ai.content, ai.messageType, ai.options || []);
                }
            });
            if (aiResponses.length > 0) {
                currentState = aiResponses[aiResponses.length - 1].chatState;
            }
            updateDebugState();
        } catch (err) {
            console.error("서버 전송 오류:", err);
            addMessage('ai', '⚠️ 서버 전송에 실패했습니다.');
        } finally {
            setSendButtonState(true);
            showLoading(false);
            messageInput.focus();
        }
    }

    function addMessage(sender, text, messageType = 'TEXT', options = []) {
        const escapedText = text.replace(/</g, "&lt;").replace(/>/g, "&gt;");
        let contentHTML = `<div class="message-content">${escapedText}</div>`;

        if (messageType === 'SELECTION') {
            const buttonsHTML = options.map((opt, idx) =>
                `<button class="quick-btn" onclick="sendMessageWrapper('${idx + 1}', ${bookId})">${idx + 1}. ${opt}</button>`
            ).join('');
            contentHTML = `<div class="message-content">${escapedText}<div class="quick-actions">${buttonsHTML}</div></div>`;
        } else if (messageType === 'RATING') {
            let starsHTML = `<div class="rating-stars" onmouseout="styleStars(this, 0)">`;
            for (let i = 1; i <= 5; i++) {
                starsHTML += `<span id="star_${i}" onmouseover="styleStars(this.parentElement, ${i})" onclick="sendMessageWrapper('${i}', ${bookId})">☆</span>`;
            }
            starsHTML += `</div>`;
            contentHTML = `<div class="message-content">${escapedText}<br>${starsHTML}</div>`;
        }

        const messageDiv = $('<div>').addClass('message').addClass(sender).html(contentHTML);
        chatMessages.append(messageDiv);
        chatMessages.scrollTop(chatMessages.prop("scrollHeight"));
    }

    window.sendMessageWrapper = (message, bookIdParam) => sendMessage(message, bookIdParam);
    window.styleStars = (container, rating) => {
        for (let i = 1; i <= 5; i++) {
            $(container).find(`#star_${i}`).text(i <= rating ? '★' : '☆');
        }
    };

    async function loadChatHistory(currentBookId) {
        showLoading(true);
        try {
            const history = await apiCall(`/api/chat/history?bookId=${currentBookId}`, 'GET');
            chatMessages.empty();
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
            // 대화 기록 로딩이 완료된 후, 대화창이 비어있으면 새 대화를 시작합니다.
                                                            if (chatMessages.children().length === 0) {
                                                                startNewChat(currentBookId);
                                                            }        }
    }

    function startNewChat(currentBookId) {
        if (initialMessageSent) return;
        initialMessageSent = true;

        currentState = 'WAITING_USER_SELECT_FEATURE';
        sendMessage('', currentBookId);
    }

    async function deleteChatHistoryAndRestart(currentBookId) {
        if (!confirm('모든 대화 기록을 삭제하고 새로 시작하시겠습니까?')) return;

        initialMessageSent = false;

        showLoading(true);
        try {
            await apiCall(`/api/chat/history?bookId=${currentBookId}`, 'DELETE');
            chatMessages.empty();
            startNewChat(currentBookId);
        } catch (err) {
            showError("이력 삭제 실패");
        } finally {
            showLoading(false);
        }
    }

    function updateDebugState() {
        debugStateEl.text(currentState || 'N/A');
        newChatButton.css('display', currentState !== 'WAITING_USER_SELECT_FEATURE' ? 'inline-block' : 'none');
    }

    function showLoading(show) {
        loadingIndicator.css('display', show ? 'block' : 'none');
    }

    function setSendButtonState(enabled) {
        sendButton.prop('disabled', !enabled);
        sendButton.text(enabled ? '전송' : '전송 중...');
    }

    // Initial Load
    loadChatHistory(bookId);
}