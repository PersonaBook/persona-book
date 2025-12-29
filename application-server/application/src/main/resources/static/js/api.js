// api.js

function getAuthHeader() {
    const token = localStorage.getItem('accessToken');
    return token ? { 'Authorization': 'Bearer ' + token } : {};
}

function apiCall(url, method, data) {
    const headers = getAuthHeader();
    const config = {
        method: method,
        headers: headers
    };

    if (data) {
        config.headers['Content-Type'] = 'application/json';
        config.body = JSON.stringify(data);
    }

    return new Promise((resolve, reject) => {
        fetch(url, config)
            .then(response => {
                if (!response.ok) {
                    // response.ok가 false이면 HTTP 오류 (4xx, 5xx)
                    // 오류 메시지를 common.js의 handleApiError로 넘겨주기 위해 Response 객체를 reject
                    return response.json().then(errorData => {
                        const error = new Error(errorData.message || 'API request failed');
                        error.response = response; // 원본 Response 객체 저장
                        error.status = response.status;
                        reject(error);
                    }).catch(() => {
                        // JSON 파싱 실패시, 일반 에러로 처리
                        const error = new Error(response.statusText || 'Network response was not ok.');
                        error.response = response;
                        error.status = response.status;
                        reject(error);
                    });
                }
                return response.json();
            })
            .then(jsonResponse => {
                // Assuming the backend sends a consistent response structure like { success: boolean, data: ..., message: ... }
                if (jsonResponse.success) {
                    resolve(jsonResponse.data);
                } else {
                    reject(new Error(jsonResponse.message || 'API request failed'));
                }
            })
            .catch(error => {
                // Network errors or errors from the .then(response => ...) block
                // Use the centralized error handler from common.js if available
                if (typeof handleApiError === 'function') {
                    // Pass the error and response object directly
                    handleApiError(error, error.response);
                }
                reject(error);
            });
    });
}

// --- Chat API ---
function sendChatMessage(payload) {
    return apiCall('/api/chat/send', 'POST', payload);
}

function getChatHistory(userId, bookId) {
    return apiCall(`/api/chat/history?userId=${userId}&bookId=${bookId}`, 'GET');
}

function deleteChatHistory(userId, bookId) {
    return apiCall(`/api/chat/history?userId=${userId}&bookId=${bookId}`, 'DELETE');
}

function pingServer() {
    return apiCall('/api/chat/ping', 'GET');
}

// --- User API ---
function updateUserProfile(payload) {
    return apiCall('/api/user/profile', 'PATCH', payload);
}
