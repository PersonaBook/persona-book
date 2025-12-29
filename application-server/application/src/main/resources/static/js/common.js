// 이 파일은 애플리케이션 전반에서 사용되는 공통 유틸리티 함수 및 설정을 정의합니다.
// API 에러 처리, 인증 토큰 관리, 그리고 UI의 인증 상태 관리 (HeaderAuthManager) 등의 기능을 포함합니다.

// 공통 에러 처리 함수
async function handleApiError(error, response = null, defaultMessage = '오류가 발생했습니다.') {
    let errorMessage = defaultMessage;
    let statusCode = 0;

    if (response) {
        statusCode = response.status;
        try {
            const errorData = await response.json();
            if (errorData.message) {
                errorMessage = errorData.message;
            } else if (errorData.detail) { // FastAPI often uses 'detail' for error messages
                errorMessage = errorData.detail;
            }
        } catch (e) {
            // JSON 파싱 실패시, response.statusText 사용
            errorMessage = response.statusText || defaultMessage;
        }
    } else if (error instanceof Error) {
        // 네트워크 오류 또는 기타 자바스크립트 오류
        errorMessage = error.message;
        // statusCode는 0 또는 undefined로 남을 수 있음
    }

    // 인증 관련 에러 처리
    if (statusCode === 401) {
        alert('로그인이 필요합니다.');
        window.location.href = '/user/login';
        return;
    }

    // 권한 관련 에러 처리
    if (statusCode === 403) {
        alert('접근 권한이 없습니다.');
        return;
    }

    // 기타 에러 처리
    alert(errorMessage);
}

// api.js의 apiCall 함수에서 에러 발생 시 handleApiError 호출 방식도 변경되어야 합니다.
// 예를 들어: .catch(error => { handleApiError(error, error.response); });

// 토큰 관련 공통 함수
function getAuthToken() {
    // localStorage 확인
    return localStorage.getItem('accessToken') || '';
}

function logout() {
    // 클라이언트 토큰 정리
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');

    window.location.href = '/auth/login';
}

// 토큰 만료 확인 함수
function isTokenExpired(token) {
    if (!token) return true;
    
    try {
        // JWT 토큰을 디코딩하여 만료시간 확인
        const payload = JSON.parse(atob(token.split('.')[1]));
        const currentTime = Math.floor(Date.now() / 1000);
        return payload.exp < currentTime;
    } catch (e) {
        return true; // 디코딩 실패시 만료된 것으로 처리
    }
}

// 자동 로그아웃 함수
function autoLogout() {
    // 토큰 정리
    localStorage.removeItem('accessToken');

    alert('로그인이 만료되었습니다. 다시 로그인해주세요.');
    window.location.href = '/auth/login';
}

// 헤더 인증 상태 관리 모듈
const HeaderAuthManager = {
    // DOM 요소 캐싱
    elements: {
        loginNav: null,
        loginJoin: null,
        logoutNav: null,
        logoutMenu: null,
    },
    
    // 초기화
    init() {
        this.cacheElements();
        this.updateUI();
        this.bindEvents();
        this.startTokenExpiryCheck();
    },
    
    // DOM 요소 캐싱
    cacheElements() {
        this.elements.loginNav = document.getElementById('login-nav');
        this.elements.loginJoin = document.getElementById('login-join');
        this.elements.logoutNav = document.getElementById('logout-nav');
        this.elements.logoutMenu = document.getElementById('logout-menu');
    },
    
    // 토큰 상태 확인 (만료 체크 포함)
    hasValidToken() {
        const token = getAuthToken();
        if (!token || token.trim() === '') {
            return false;
        }
        
        // 토큰 만료 확인
        if (isTokenExpired(token)) {
            autoLogout();
            return false;
        }
        
        return true;
    },
    
    // UI 업데이트
    updateUI() {
        const isLoggedIn = this.hasValidToken();
        this.toggleElement(this.elements.loginNav, !isLoggedIn);
        this.toggleElement(this.elements.loginJoin, !isLoggedIn);
        this.toggleElement(this.elements.logoutNav, isLoggedIn);
        this.toggleElement(this.elements.logoutMenu, isLoggedIn);
    },
    
    // 요소 표시/숨김 토글
    toggleElement(element, show) {
        if (element) {
            element.style.display = show ? 'block' : 'none';
        }
    },
    
    // 토큰 만료 주기적 확인 시작
    startTokenExpiryCheck() {
        // 1분마다 토큰 만료 확인
        setInterval(() => {
            const token = getAuthToken();
            if (token && isTokenExpired(token)) {
                autoLogout();
            }
        }, 60000); // 1분 = 60000ms
    },
    
    // 이벤트 바인딩
    bindEvents() {
        // 페이지 포커스 이벤트
        $(window).on('focus', () => this.updateUI());
        
        // 탭 전환 이벤트
        $(document).on('visibilitychange', () => {
            if (!document.hidden) {
                this.updateUI();
            }
        });
        
        // localStorage/sessionStorage 변경 이벤트 (다른 탭에서의 변경 감지)
        $(window).on('storage', (e) => {
            if (e.originalEvent.key === 'accessToken') {
                this.updateUI();
            }
        });
    },
    
    // 강제 UI 업데이트 (외부에서 호출 가능)
    refresh() {
        this.updateUI();
    }
};

// common.js 파일의 맨 마지막 부분

document.addEventListener('DOMContentLoaded', () => {
    HeaderAuthManager.init();
});