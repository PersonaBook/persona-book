// api.js

function getAuthToken() {
    return localStorage.getItem('accessToken');
}

function getAuthHeader() {
    const token = getAuthToken();
    return token ? { 'Authorization': 'Bearer ' + token } : {};
}

/**
 * 공통 API 호출 함수
 * ApiResponseDto: { success: boolean, code: string, message: string, data: T }
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

        // 응답 본문(JSON) 파싱 시도
        let jsonResponse;
        try {
            jsonResponse = await response.json();
        } catch (e) {
            jsonResponse = null; // JSON이 아닌 경우 (예: 404 HTML 페이지 등)
        }

        // 1. 서버가 ApiResponseDto 형식으로 응답을 준 경우
        if (jsonResponse && typeof jsonResponse.success === 'boolean') {
            if (jsonResponse.success) {
                return jsonResponse.data; // 성공 시 data만 반환
            } else {
                // 비즈니스 로직 실패 (success: false)
                const error = new Error(jsonResponse.message || '요청 처리 실패');
                error.code = jsonResponse.code; // DTO의 code ("400", "404" 등)
                error.status = response.status; // HTTP 상태 코드
                throw error;
            }
        }

        // 2. ApiResponseDto 형식이 아닌 에러 (예: Spring Security 필터 차단, 500 HTML 에러 등)
        if (!response.ok) {
            const error = new Error(jsonResponse?.message || response.statusText || '서버 통신 오류');
            error.status = response.status;
            throw error;
        }

        // 3. 드물지만 성공했는데 JSON이 아니고 ApiResponseDto도 아닌 경우
        return jsonResponse;

    } catch (error) {
        // 호출부에서 catch 하지 않으면 공통 핸들러로 넘김
        // (단, auth.js처럼 개별적으로 try-catch 하는 곳은 여기서 throw 된 것을 잡아서 처리함)
        if (typeof handleApiError === 'function') {
            // 여기서는 throw만 하고, 실제 처리는 호출부나 전역 핸들러에 위임하는 패턴 권장
            // 하지만 편의를 위해 여기서 로그만 찍고 재전송
        }
        console.error(`[API Error] ${method} ${url}`, error);
        throw error;
    }
}