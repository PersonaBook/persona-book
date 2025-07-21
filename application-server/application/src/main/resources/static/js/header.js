document.addEventListener('DOMContentLoaded', function() {
    const loginButton = document.getElementById('login-button');
    const logoutButton = document.getElementById('logout-button');

    // 기본적으로 로그아웃 버튼 숨김
    if (logoutButton) logoutButton.style.display = 'none';

    const accessToken = localStorage.getItem('accessToken');
    console.log('Access Token:', accessToken ? 'Exists' : 'Does not exist');

    if (accessToken) {
        if (logoutButton) logoutButton.style.display = 'inline-block';
        if (loginButton) loginButton.style.display = 'none';
    } else {
        if (logoutButton) logoutButton.style.display = 'none';
        if (loginButton) loginButton.style.display = 'inline-block';
    }

    if (logoutButton) {
        logoutButton.addEventListener('click', function(event) {
            event.preventDefault();
            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken');
            window.location.href = '/pdfMain';
        });
    }
});

// 공통 fetch 래퍼: accessToken 만료 시 refreshToken으로 자동 갱신
async function authFetch(url, options = {}) {
    const accessToken = localStorage.getItem('accessToken');
    options.headers = options.headers || {};
    if (accessToken) {
        options.headers['Authorization'] = 'Bearer ' + accessToken;
    }
    let response = await fetch(url, options);
    if (response.status === 401 || response.status === 403) {
        const refreshToken = localStorage.getItem('refreshToken');
        if (refreshToken) {
            const refreshRes = await fetch('/api/auth/refreshtoken', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refreshToken })
            });
            if (refreshRes.ok) {
                const data = await refreshRes.json();
                if (data.token) {
                    localStorage.setItem('accessToken', data.token);
                    options.headers['Authorization'] = 'Bearer ' + data.token;
                    return fetch(url, options);
                }
            }
        }
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        window.location.href = '/login';
        throw new Error('로그인 세션이 만료되었습니다. 다시 로그인 해주세요.');
    }
    return response;
}
// 사용 예시: authFetch('/myPage', { method: 'GET' }).then(res => res.json()).then(data => { ... });
