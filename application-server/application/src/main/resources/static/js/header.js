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

// Floating Chatbot & Memo Logic
window.addEventListener('DOMContentLoaded', function() {
  // HTML 템플릿 (최소화/최대화/닫기 버튼 포함)
  const chatbotTemplate = () => `
    <div class="floating-window card shadow" id="chatbot-window" style="width: 350px; position: fixed; bottom: 100px; right: 24px; z-index: 1060;">
      <div class="card-header d-flex justify-content-between align-items-center p-2 bg-info text-white">
        <span><i class="fa fa-comments"></i> Live Chat</span>
        <div>
          <button class="btn btn-sm btn-light me-1" title="Minimize" onclick="windowMinimize('chatbot-window')"><i class="fa fa-minus"></i></button>
          <button class="btn btn-sm btn-light me-1" title="Maximize" onclick="windowMaximize('chatbot-window')"><i class="fa fa-square-o"></i></button>
          <button class="btn btn-sm btn-light" title="Close" onclick="windowClose('chatbot-window')"><i class="fa fa-times"></i></button>
        </div>
      </div>
      <div class="card-body" style="max-height: 400px; overflow-y: auto;">
        <!-- 채팅 UI 내용 (간략화) -->
        <div class="d-flex flex-row justify-content-start mb-4">
          <img src="https://mdbcdn.b-cdn.net/img/Photos/new-templates/bootstrap-chat/ava1-bg.webp" alt="avatar 1" style="width: 45px; height: 100%;">
          <div class="p-3 ms-3" style="border-radius: 15px; background-color: rgba(57, 192, 237,.2);">
            <p class="small mb-0">Hello and thank you for visiting MDBootstrap. Please click the video below.</p>
          </div>
        </div>
        <div class="d-flex flex-row justify-content-end mb-4">
          <div class="p-3 me-3 border bg-body-tertiary" style="border-radius: 15px;">
            <p class="small mb-0">Thank you, I really like your product.</p>
          </div>
          <img src="https://mdbcdn.b-cdn.net/img/Photos/new-templates/bootstrap-chat/ava2-bg.webp" alt="avatar 1" style="width: 45px; height: 100%;">
        </div>
        <div class="d-flex flex-row justify-content-start mb-4">
          <img src="https://mdbcdn.b-cdn.net/img/Photos/new-templates/bootstrap-chat/ava1-bg.webp" alt="avatar 1" style="width: 45px; height: 100%;">
          <div class="ms-3" style="border-radius: 15px;">
            <div class="bg-image">
              <img src="https://mdbcdn.b-cdn.net/img/Photos/new-templates/bootstrap-chat/screenshot1.webp" style="border-radius: 15px;" alt="video">
              <a href="#"><div class="mask"></div></a>
            </div>
          </div>
        </div>
        <div class="d-flex flex-row justify-content-start mb-4">
          <img src="https://mdbcdn.b-cdn.net/img/Photos/new-templates/bootstrap-chat/ava1-bg.webp" alt="avatar 1" style="width: 45px; height: 100%;">
          <div class="p-3 ms-3" style="border-radius: 15px; background-color: rgba(57, 192, 237,.2);">
            <p class="small mb-0">...</p>
          </div>
        </div>
        <div class="form-outline">
          <textarea class="form-control bg-body-tertiary" rows="2"></textarea>
          <label class="form-label">Type your message</label>
        </div>
      </div>
    </div>
  `;

  const memoTemplate = () => `
    <div class="floating-window card shadow" id="memo-window" style="width: 300px; position: fixed; bottom: 100px; right: 24px; z-index: 1060;">
      <div class="card-header d-flex justify-content-between align-items-center p-2 bg-warning text-dark">
        <span><i class="fa fa-sticky-note"></i> 메모</span>
        <div>
          <button class="btn btn-sm btn-light me-1" title="Minimize" onclick="windowMinimize('memo-window')"><i class="fa fa-minus"></i></button>
          <button class="btn btn-sm btn-light me-1" title="Maximize" onclick="windowMaximize('memo-window')"><i class="fa fa-square-o"></i></button>
          <button class="btn btn-sm btn-light" title="Close" onclick="windowClose('memo-window')"><i class="fa fa-times"></i></button>
        </div>
      </div>
      <div class="card-body" style="max-height: 300px; overflow-y: auto;">
        <ul class="notes list-unstyled">
          <li>
            <div class="rotate-1 lazur-bg p-2 mb-2 rounded">
              <small>12:03:28 12-04-2014</small>
              <h6>Awesome title</h6>
              <p>The years, sometimes by accident, sometimes on purpose (injected humour and the like).</p>
              <a href="#" class="text-danger pull-right"><i class="fa fa-trash-o"></i></a>
            </div>
          </li>
          <li>
            <div class="rotate-2 red-bg p-2 mb-2 rounded">
              <small>12:03:28 12-04-2014</small>
              <h6>Awesome date</h6>
              <p>The years, sometimes by accident, sometimes on purpose (injected humour and the like).</p>
              <a href="#" class="text-danger pull-right"><i class="fa fa-trash-o"></i></a>
            </div>
          </li>
          <li>
            <div class="rotate-1 yellow-bg p-2 mb-2 rounded">
              <small>12:03:28 12-04-2014</small>
              <h6>Awesome project</h6>
              <p>The years, sometimes by accident, sometimes on purpose (injected humour and the like).</p>
              <a href="#" class="text-danger pull-right"><i class="fa fa-trash-o"></i></a>
            </div>
          </li>
        </ul>
      </div>
    </div>
  `;

  // 창 상태 관리 함수
  window.windowMinimize = function(id) {
    const win = document.getElementById(id);
    if (win) win.querySelector('.card-body').style.display = 'none';
  };
  window.windowMaximize = function(id) {
    const win = document.getElementById(id);
    if (win) {
      if (win.classList.contains('maximized')) {
        win.style.width = win.dataset.origWidth;
        win.style.height = win.dataset.origHeight;
        win.classList.remove('maximized');
      } else {
        win.dataset.origWidth = win.style.width;
        win.dataset.origHeight = win.style.height;
        win.style.width = '90vw';
        win.style.height = '90vh';
        win.classList.add('maximized');
      }
    }
  };
  window.windowClose = function(id) {
    const win = document.getElementById(id);
    if (win) win.remove();
  };

  // 버튼 이벤트
  const widgets = document.getElementById('floating-widgets');
  const chatBtn = document.getElementById('open-chatbot');
  const memoBtn = document.getElementById('open-memo');
  if (chatBtn) {
    chatBtn.onclick = function() {
      const w = window.screen.availWidth;
      const h = window.screen.availHeight;
      window.open('/chat', 'chatbotWindow', `width=${w},height=${h},left=0,top=0,resizable=yes,scrollbars=yes`);
    };
  }
  if (memoBtn) {
    memoBtn.onclick = function() {
      alert('메모 기능은 추후 구현 예정입니다.');
    };
  }
});

// floating-window 드래그 이동 기능 제거됨
