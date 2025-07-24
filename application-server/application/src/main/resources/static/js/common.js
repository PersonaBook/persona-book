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
});