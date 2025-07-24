// 공통 에러 처리 함수
function handleApiError(xhr, defaultMessage = '오류가 발생했습니다.') {
    let errorMessage = defaultMessage;
    
    if (xhr.responseJSON && xhr.responseJSON.message) {
        errorMessage = xhr.responseJSON.message;
    } else if (xhr.responseText) {
        try {
            const errorData = JSON.parse(xhr.responseText);
            if (errorData.message) {
                errorMessage = errorData.message;
            }
        } catch (e) {
            // JSON 파싱 실패시 기본 메시지 사용
        }
    }
    
    // 인증 관련 에러 처리
    if (xhr.status === 401) {
        alert('로그인이 필요합니다.');
        window.location.href = '/user/login';
        return;
    }
    
    // 권한 관련 에러 처리
    if (xhr.status === 403) {
        alert('접근 권한이 없습니다.');
        return;
    }
    
    // 기타 에러 처리
    alert(errorMessage);
}

// 토큰 관련 공통 함수
function getAuthToken() {
    return localStorage.getItem('accessToken') || '';
}

function logout() {
    // 서버 로그아웃 API 호출
    $.ajax({
        url: '/api/auth/logout',
        type: 'POST',
        headers: {
            'Authorization': 'Bearer ' + getAuthToken()
        },
        success: function() {
            // 클라이언트 토큰 정리
            localStorage.clear();
            sessionStorage.clear();
            
            // 쿠키도 삭제
            document.cookie.split(";").forEach(function(c) { 
                document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/"); 
            });
            
            window.location.href = '/';
        },
        error: function() {
            // 에러가 발생해도 클라이언트 정리 후 리다이렉트
            localStorage.clear();
            sessionStorage.clear();
            window.location.href = '/';
        }
    });
}

// 헤더 인증 상태 관리 모듈
const HeaderAuthManager = {
    // DOM 요소 캐싱
    elements: {
        loginNav: null,
        logoutNav: null
    },
    
    // 초기화
    init() {
        this.cacheElements();
        this.updateUI();
        this.bindEvents();
    },
    
    // DOM 요소 캐싱
    cacheElements() {
        this.elements.loginNav = document.getElementById('login-nav');
        this.elements.logoutNav = document.getElementById('logout-nav');
    },
    
    // 토큰 상태 확인
    hasValidToken() {
        const token = getAuthToken();
        return token && token.trim() !== '';
    },
    
    // UI 업데이트
    updateUI() {
        const isLoggedIn = this.hasValidToken();
        this.toggleElement(this.elements.loginNav, !isLoggedIn);
        this.toggleElement(this.elements.logoutNav, isLoggedIn);
    },
    
    // 요소 표시/숨김 토글
    toggleElement(element, show) {
        if (element) {
            element.style.display = show ? 'block' : 'none';
        }
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
        
        // localStorage 변경 이벤트 (다른 탭에서의 변경 감지)
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

// 하위 호환성을 위한 기존 함수
function checkTokenAndUpdateUI() {
    HeaderAuthManager.updateUI();
}

$(document).ready(function(){
    /* section layout 최소 height */
    function adjustSectionHeight() {
        const vh = $(window).outerHeight();
        const headerH = $('header').outerHeight() || 0;
        $('section').css('min-height', vh - headerH);
        $('section > div').css('min-height', vh - headerH);
        $('section > div > div.container').css('min-height', vh - headerH);
        $('#bookData').css('min-height', vh - headerH);
    }
  
    adjustSectionHeight();
    $(window).on('resize', adjustSectionHeight);
    
    // 헤더 인증 관리자 초기화
    HeaderAuthManager.init();
    
    // URL에서 토큰 파라미터 처리
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    const shouldRefresh = urlParams.get('refresh') === 'true';
    
    // 토큰이 있으면 localStorage에 저장
    if (token) {
        localStorage.setItem('accessToken', token);
        // URL에서 token 파라미터 제거
        const cleanUrl = window.location.pathname + window.location.search
            .replace(/[?&]token=[^&]*/, '')
            .replace(/[?&]refresh=true/, '')
            .replace(/^\?$/, '');
        history.replaceState(null, '', cleanUrl);
    }
    
    // 로그인 후 리다이렉트 시 새로고침
    if (shouldRefresh) {
        setTimeout(() => {
            window.location.reload();
        }, 100);
    }
});