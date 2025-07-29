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
    // sessionStorage 우선 확인 (단기 토큰)
    const sessionToken = sessionStorage.getItem('accessToken');
    if (sessionToken) {
        return sessionToken;
    }
    // localStorage 확인 (장기 토큰)
    return localStorage.getItem('accessToken') || '';
}

// 토큰 저장 함수
function setAuthToken(token, rememberMe) {
    if (rememberMe) {
        // 로그인 유지 체크 시 localStorage에 저장 (24시간)
        localStorage.setItem('accessToken', token);
        sessionStorage.removeItem('accessToken'); // 중복 방지
    } else {
        // 체크 안함 시 sessionStorage에 저장 (30분, 탭 닫으면 삭제)
        sessionStorage.setItem('accessToken', token);
        localStorage.removeItem('accessToken'); // 중복 방지
    }
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
    sessionStorage.removeItem('accessToken');
    
    alert('로그인이 만료되었습니다. 다시 로그인해주세요.');
    window.location.href = '/user/login';
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

// 하위 호환성을 위한 기존 함수
function checkTokenAndUpdateUI() {
    HeaderAuthManager.updateUI();
}

// ID 찾기 함수
function findUserId(userName, email) {
    return $.ajax({
        url: '/api/auth/findId',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            userName: userName,
            email: email
        }),
        success: function(response) {
            console.log('응답:', response);
            if (response.status === 'OK') {
                alert(response.message);
                window.location.href = '/';
            } else {
                alert(response.message || 'ID 찾기에 실패했습니다.');
            }
        },
        error: function(xhr) {
            handleApiError(xhr, 'ID 찾기 중 오류가 발생했습니다.');
        }
    });
}

// 비밀번호 리셋 함수
function resetPassword(userName, email, newPassword) {
    return $.ajax({
        url: '/api/findPassword/reset',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            userName: userName,
            email: email,
            newPassword: newPassword
        }),
        success: function(response) {
            console.log('응답:', response);
            if (response.status === 'OK' || response.message === '비밀번호가 성공적으로 변경되었습니다.') {
                alert('비밀번호 변경에 성공하였습니다');
                window.location.href = '/';
            } else {
                alert(response.message || '비밀번호 변경에 실패했습니다.');
            }
        },
        error: function(xhr) {
            handleApiError(xhr, '비밀번호 변경 중 오류가 발생했습니다.');
        }
    });
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
    
    // 비밀번호 리셋 폼 이벤트 처리
    const resetPasswordForm = document.getElementById('resetPasswordForm');
    if (resetPasswordForm) {
        resetPasswordForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const userName = document.getElementById('name').value;
            const email = document.getElementById('email').value;
            const verificationCode = document.getElementById('verificationCode').value;
            const newPassword = document.getElementById('newPassword').value;
            const confirmNewPassword = document.getElementById('confirmNewPassword').value;
            
            // 비밀번호 확인 검증
            if (newPassword !== confirmNewPassword) {
                alert('새로운 비밀번호와 비밀번호 확인이 일치하지 않습니다.');
                return;
            }
            
            // 비밀번호 리셋 함수 호출
            resetPassword(userName, email, newPassword);
        });
    }
    
    // ID 찾기 폼 이벤트 처리
    const idInquiryForm = document.getElementById('form_area');
    if (idInquiryForm) {
        idInquiryForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const userName = document.getElementById('name').value;
            const email = document.getElementById('email').value;
            
            // ID 찾기 함수 호출
            findUserId(userName, email);
        });
    }
    
    // URL에서 토큰 파라미터 처리
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    const rememberMe = urlParams.get('rememberMe') === 'true';
    const shouldRefresh = urlParams.get('refresh') === 'true';
    
    // 토큰이 있으면 rememberMe에 따라 저장
    if (token) {
        setAuthToken(token, rememberMe);
        // URL에서 파라미터들 제거
        const cleanUrl = window.location.pathname + window.location.search
            .replace(/[?&]token=[^&]*/, '')
            .replace(/[?&]rememberMe=[^&]*/, '')
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