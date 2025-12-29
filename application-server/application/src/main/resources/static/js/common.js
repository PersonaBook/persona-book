// common.js

/**
 * 전역 에러 처리 함수
 */
function handleApiError(error) {
    console.error('API Error:', error);

    const statusCode = error.status;
    const message = error.message || '오류가 발생했습니다.';

    // 1. 인증 에러 (401)
    if (statusCode === 401) {
        alert('세션이 만료되었거나 로그인이 필요합니다.');
        logout();
        return;
    }

    // 2. 권한 에러 (403)
    if (statusCode === 403) {
        alert('접근 권한이 없습니다.');
        return;
    }

    // 3. AI 서버 장애 (503) - ChatService에서 던진 에러 대응
    if (statusCode === 503) {
        alert('현재 AI 서버 연결이 원활하지 않습니다. 잠시 후 다시 시도해주세요.');
        return;
    }

    // 4. 기타 에러
    alert(message);
}

function logout() {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    window.location.href = '/auth/login';
}

function isTokenExpired(token) {
    if (!token) return true;
    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        const currentTime = Math.floor(Date.now() / 1000);
        return payload.exp < currentTime;
    } catch (e) {
        return true;
    }
}

// 헤더 인증 상태 관리
const HeaderAuthManager = {
    init() {
        this.updateUI();
        this.bindEvents();
        this.startTokenExpiryCheck();
    },

    updateUI() {
        const token = localStorage.getItem('accessToken');
        const isLoggedIn = token && !isTokenExpired(token);

        const loginElements = document.querySelectorAll('#login-nav, #login-join');
        const logoutElements = document.querySelectorAll('#logout-nav, #logout-menu');

        loginElements.forEach(el => el.style.display = isLoggedIn ? 'none' : 'block');
        logoutElements.forEach(el => el.style.display = isLoggedIn ? 'block' : 'none');
    },

    bindEvents() {
        window.addEventListener('focus', () => this.updateUI());
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden) this.updateUI();
        });
        window.addEventListener('storage', (e) => {
            if (e.key === 'accessToken') this.updateUI();
        });
    },

    startTokenExpiryCheck() {
        setInterval(() => {
            const token = localStorage.getItem('accessToken');
            if (token && isTokenExpired(token)) {
                logout();
            }
        }, 60000);
    },

    refresh() { this.updateUI(); }
};

document.addEventListener('DOMContentLoaded', () => HeaderAuthManager.init());