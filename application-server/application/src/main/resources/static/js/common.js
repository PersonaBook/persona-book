// common.js

/**
 * 전역 에러 처리 함수
 * error 객체는 message, code(DTO 문자열), status(HTTP 숫자)를 가질 수 있음
 */
function handleApiError(error) {
    const message = error.message || '알 수 없는 오류가 발생했습니다.';

    // HTTP Status 또는 DTO Code를 숫자로 변환하여 체크
    // DTO Code가 "401" 문자열로 올 수 있으므로 parseInt 처리
    const statusCode = error.status || parseInt(error.code || '0', 10);

    console.warn('HandleApiError:', { message, statusCode });

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

    // 3. 서버 내부 오류 (500)
    if (statusCode === 500) {
        alert('서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.');
        return;
    }

    // 4. 그 외 (400 Bad Request, 404 Not Found 등)
    // 사용자에게 서버에서 보낸 메시지(errorCode.getMessage())를 그대로 보여줌
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
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(window.atob(base64).split('').map(function(c) {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));

        const payload = JSON.parse(jsonPayload);
        const currentTime = Math.floor(Date.now() / 1000);
        return payload.exp < currentTime;
    } catch (e) {
        return true;
    }
}

function setValidationMessage(inputId, isValid, message) {
    const input = document.getElementById(inputId);
    const errorDiv = document.getElementById(inputId + 'Error');
    const successDiv = document.getElementById(inputId + 'Success');

    if (!input) return;

    if (isValid) {
        input.classList.remove('is-invalid');
        input.classList.add('is-valid');
        if (errorDiv) errorDiv.style.display = 'none';
        if (successDiv) {
            successDiv.textContent = message;
            successDiv.style.display = 'block';
        }
    } else {
        input.classList.remove('is-valid');
        input.classList.add('is-invalid');
        if (successDiv) successDiv.style.display = 'none';
        if (errorDiv) {
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
        }
    }
}

// 유효성 검사 함수들
function validateEmail(email) {
    const re = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(String(email).toLowerCase());
}
function validateName(name) { return name && name.trim().length > 0; }
function validatePassword(password) { return password && password.length >= 8; }
function validateConfirmPassword(password, confirmPassword) { return password === confirmPassword; }

// 헤더 인증 관리자
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
            if (token && isTokenExpired(token)) logout();
        }, 60000);
    },
    refresh() { this.updateUI(); }
};

document.addEventListener('DOMContentLoaded', () => HeaderAuthManager.init());