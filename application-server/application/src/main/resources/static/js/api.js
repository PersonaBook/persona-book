// api.js

function getAuthHeader() {
    const token = localStorage.getItem('accessToken');
    return token ? { 'Authorization': 'Bearer ' + token } : {};
}

/**
 * 공통 API 호출 함수
 * ApiResponseDto { success, data, message } 구조를 처리합니다.
 */
async function apiCall(url, method, data) {
    const headers = getAuthHeader();
    const config = {
        method: method,
        headers: headers
    };

    if (data) {
        config.headers['Content-Type'] = 'application/json';
        config.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(url, config);

        // HTTP 상태 코드 에러 처리 (4xx, 5xx)
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            const error = new Error(errorData.message || '요청 실패');
            error.status = response.status;
            error.response = response;
            throw error;
        }

        const jsonResponse = await response.json();

        // ApiResponseDto의 success 필드 확인
        if (jsonResponse.success) {
            return jsonResponse.data; // 성공 시 data만 반환
        } else {
            throw new Error(jsonResponse.message || 'API 응답 오류');
        }
    } catch (error) {
        // common.js의 전역 에러 핸들러 호출
        if (typeof handleApiError === 'function') {
            handleApiError(error);
        }
        throw error;
    }
}

// --- Chat API (백엔드 컨트롤러 규격에 맞춤) ---
function sendChatMessage(payload) {
    // 이제 payload 안에 userId를 명시할 필요가 없습니다. (서버가 무시/덮어씀)
    return apiCall('/api/chat/send', 'POST', payload);
}

function getChatHistory(bookId) {
    return apiCall(`/api/chat/history?bookId=${bookId}`, 'GET');
}

function deleteChatHistory(bookId) {
    return apiCall(`/api/chat/history?bookId=${bookId}`, 'DELETE');
}

function pingServer() {
    return apiCall('/api/chat/ping', 'GET');
}

// --- User API ---
function updateUserProfile(payload) {
    return apiCall('/api/user/profile', 'PATCH', payload);
}