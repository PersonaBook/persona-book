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

function isLoggedIn() {
    return getAuthToken() !== '';
}

function logout() {
    localStorage.clear(); // 모든 localStorage 데이터 삭제
    sessionStorage.clear(); // 모든 sessionStorage 데이터 삭제
    
    // 쿠키도 삭제
    document.cookie.split(";").forEach(function(c) { 
        document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/"); 
    });
    
    window.location.href = '/';
}

$(document).ready(function(){
    /* section layout 최소 height */
    var header = $('header').outerHeight();
    var section = $("section").outerHeight();
    var footer = $("footer").outerHeight();

    $("section").css('minHeight', (section - (header + footer)) + 'px');
    
    // 로그인 상태에 따라 버튼 보이기/숨기기
    if (isLoggedIn()) {
        $('#logout-nav').show();
        $('#login-nav').hide();
    } else {
        $('#login-nav').show();
        $('#logout-nav').hide();
    }
});