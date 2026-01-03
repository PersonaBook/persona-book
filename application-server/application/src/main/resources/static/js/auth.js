// auth.js

// --- Auth API ---
function login(payload) {
    return apiCall('/api/auth/login', 'POST', payload);
}

function register(payload) {
    return apiCall('/api/auth/register', 'POST', payload);
}

function findId(payload) {
    return apiCall('/api/auth/id/find', 'POST', payload);
}

function resetPassword(payload) {
    return apiCall('/api/auth/password/reset', 'POST', payload);
}

// --- Event Listeners ---
document.addEventListener('DOMContentLoaded', function () {
    initLogin();
    initRegister();
    initFindId();
    initPasswordReset();
});

/**
 * 1. 로그인 처리
 */
function initLogin() {
    const form = document.getElementById('loginForm');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const alertDiv = document.querySelector('.alert-danger');
        const alertP = alertDiv?.querySelector('p');

        if (alertDiv) alertDiv.style.display = 'none';

        try {
            // 상단 login 함수 활용
            const data = await login({ email, password });

            if (data?.token?.accessToken) {
                localStorage.setItem('accessToken', data.token.accessToken);
                if (data.token.refreshToken) {
                    localStorage.setItem('refreshToken', data.token.refreshToken);
                }

                if (typeof HeaderAuthManager !== 'undefined') HeaderAuthManager.refresh();
                window.location.href = '/';
            } else {
                throw new Error('응답에 인증 정보가 없습니다.');
            }
        } catch (error) {
            if (alertDiv && alertP) {
                alertP.textContent = error.message;
                alertDiv.style.display = 'block';
            } else {
                handleApiError(error);
            }
        }
    });
}

/**
 * 2. 회원가입 처리
 */
function initRegister() {
    const form = document.getElementById('registerForm');
    if (!form) return;

    // Datepicker 설정
    const birthInput = document.getElementById('userBirthDate');
    if (birthInput && typeof $ !== 'undefined' && $.fn.datepicker) {
        $(birthInput).datepicker({
            maxDate: "-10y", changeMonth: true, changeYear: true, yearRange: "c-100:c", dateFormat: "yy-mm-dd"
        });
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const name = document.getElementById('name').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirmPassword').value;
        const phoneNumber = document.getElementById('userPhoneNumber').value;
        const birthDate = birthInput?.value || '';
        const jobSelect = document.getElementById('userJob');
        const job = (jobSelect && jobSelect.value !== '선택...') ? jobSelect.value : null;

        // 유효성 검사 로직
        if (!validateRegister(name, email, password, confirmPassword)) return;

        const btn = document.getElementById('formBtn');
        if (btn) btn.disabled = true;

        try {
            // 상단 register 함수 활용
            await register({ name, email, password, phoneNumber, birthDate, job });
            alert('회원가입이 완료되었습니다.');
            window.location.href = '/auth/login';
        } catch (error) {
            handleApiError(error);
        } finally {
            if (btn) btn.disabled = false;
        }
    });
}

/**
 * 3. 아이디 찾기 처리
 */
function initFindId() {
    const form = document.getElementById('findIdForm');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const name = document.getElementById('name').value;
        const phoneNumber = document.getElementById('phoneNumber').value;

        if (!name || !phoneNumber) {
            alert('정보를 모두 입력해주세요.');
            return;
        }

        try {
            // 상단 findId 함수 활용
            const foundEmail = await findId({ name, phoneNumber });
            window.location.href = `/auth/id/find/success?email=${encodeURIComponent(foundEmail)}`;
        } catch (error) {
            handleApiError(error);
        }
    });
}

/**
 * 4. 비밀번호 재설정 처리
 */
function initPasswordReset() {
    const form = document.getElementById('passwordResetForm');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const name = document.getElementById('name').value;
        const email = document.getElementById('email').value;
        const newPassword = document.getElementById('newPassword').value;
        const confirmNewPassword = document.getElementById('confirmNewPassword').value;

        if (!validatePassword(newPassword)) { alert('비밀번호는 8자 이상이어야 합니다.'); return; }
        if (newPassword !== confirmNewPassword) { alert('비밀번호가 일치하지 않습니다.'); return; }

        try {
            // 상단 resetPassword 함수 활용
            await resetPassword({ name, email, newPassword });
            alert('비밀번호가 성공적으로 변경되었습니다.');
            window.location.href = '/auth/password/reset/success';
        } catch (error) {
            handleApiError(error);
        }
    });
}

/**
 * 회원가입 개별 유효성 검사 헬퍼
 */
function validateRegister(name, email, password, confirm) {
    let isValid = true;

    const checks = [
        { id: 'name', val: name, fn: validateName, msg: '이름을 입력해주세요.' },
        { id: 'email', val: email, fn: validateEmail, msg: '올바른 이메일 형식이 아닙니다.' },
        { id: 'password', val: password, fn: validatePassword, msg: '8자 이상 입력해주세요.' },
        { id: 'confirmPassword', val: confirm, fn: (c) => validateConfirmPassword(password, c), msg: '비밀번호가 일치하지 않습니다.' }
    ];

    checks.forEach(check => {
        const ok = check.fn(check.val);
        setValidationMessage(check.id, ok, ok ? '' : check.msg);
        if (!ok) isValid = false;
    });

    return isValid;
}