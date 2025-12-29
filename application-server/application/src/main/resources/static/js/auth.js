// auth.js
document.addEventListener('DOMContentLoaded', function () {
    console.log('auth.js: DOMContentLoaded event fired.');

    // 1. 공통 유틸리티 & 유효성 검사 함수 (기존 유지)
    function setValidationMessage(inputId, isValid, message) {
        const input = document.getElementById(inputId);
        const errorDiv = document.getElementById(inputId + 'Error');
        const successDiv = document.getElementById(inputId + 'Success');

        if (!input || !errorDiv || !successDiv) return;

        if (isValid) {
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
            errorDiv.style.display = 'none';
            successDiv.textContent = message;
            successDiv.style.display = 'block';
        } else {
            input.classList.remove('is-valid');
            input.classList.add('is-invalid');
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
            successDiv.style.display = 'none';
        }
    }

    function validateEmail(email) {
        const re = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        return re.test(String(email).toLowerCase());
    }

    function validateName(name) { return name && name.trim().length > 0; }
    function validatePassword(password) { return password && password.length >= 8; }
    function validateConfirmPassword(password, confirmPassword) { return password === confirmPassword; }

    // ============================================================
    // 2. 로그인 로직 (토큰 저장 문제 수정됨)
    // ============================================================
    const handleLogin = () => {
        const loginForm = document.getElementById('loginForm');
        if (!loginForm) return;

        console.log('auth.js: Login form found.');

        loginForm.addEventListener('submit', async function (event) {
            event.preventDefault();

            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const alertDiv = document.querySelector('.alert-danger'); // 폼 내부 alert 찾기
            const alertParagraph = alertDiv ? alertDiv.querySelector('p') : null;

            if (alertDiv) alertDiv.style.display = 'none';

            try {
                // apiCall: 성공 시 ApiResponseDto.data 를 반환함
                const data = await apiCall('/api/auth/login', 'POST', { email, password });

                // [디버깅] 콘솔에서 실제 데이터 구조를 확인하세요!
                console.log('Login Response Data:', data);

                // ✅ 토큰 추출 로직 강화 (구조가 다를 경우 대비)
                // Case 1: data = { accessToken: "...", refreshToken: "..." }
                // Case 2: data = { token: { accessToken: "...", ... } }
                let accessToken = null;
                let refreshToken = null;

                if (data.accessToken) {
                    accessToken = data.accessToken;
                    refreshToken = data.refreshToken;
                } else if (data.token && data.token.accessToken) {
                    accessToken = data.token.accessToken;
                    refreshToken = data.token.refreshToken;
                }

                if (accessToken) {
                    console.log('auth.js: Login successful. Saving tokens.');
                    localStorage.setItem('accessToken', accessToken);
                    localStorage.setItem('refreshToken', refreshToken || ''); // refreshToken 없으면 빈값 처리

                    if (typeof HeaderAuthManager !== 'undefined') {
                        HeaderAuthManager.refresh();
                    }

                    window.location.href = '/';
                } else {
                    // 데이터는 왔지만 accessToken 필드를 못 찾음
                    console.error('Token not found in data:', data);
                    throw new Error('서버 응답에서 토큰 정보를 찾을 수 없습니다.');
                }

            } catch (error) {
                console.error('Login Error:', error);
                const msg = error.message || '로그인에 실패했습니다.';

                if (alertParagraph && alertDiv) {
                    alertParagraph.textContent = msg;
                    alertDiv.style.display = 'block';
                } else {
                    alert(msg);
                }
            }
        });
    };
    handleLogin();

    // ============================================================
    // 3. 회원가입 로직 (이메일 인증 제거됨)
    // ============================================================
    const handleRegister = () => {
        const joinForm = document.getElementById('join_area');
        if (!joinForm) return;

        console.log('auth.js: Join form found.');

        const emailInput = document.getElementById('email');
        const userBirthDateInput = document.getElementById('userBirthDate');

        // Datepicker 초기화
        if (userBirthDateInput && typeof $ !== 'undefined' && typeof $.fn.datepicker === 'function') {
            $(userBirthDateInput).datepicker({
                maxDate: "-10y",
                changeMonth: true,
                changeYear: true,
                yearRange: "c-100:c",
                dateFormat: "yy-mm-dd"
            });
        }

        joinForm.addEventListener('submit', async function (event) {
            event.preventDefault();

            const name = document.getElementById('name').value;
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirmPassword').value;
            const email = emailInput.value;
            const userPhoneNumber = document.getElementById('userPhoneNumber').value;
            const userBirthDate = userBirthDateInput ? userBirthDateInput.value : '';
            const userJobSelect = document.getElementById('userJob');
            const userJob = userJobSelect ? userJobSelect.value : '';

            // 유효성 검사
            let allValid = true;
            if (!validateName(name)) { setValidationMessage('name', false, '이름을 입력해주세요.'); allValid = false; }
            else { setValidationMessage('name', true, '확인 완료'); }

            if (!validatePassword(password)) { setValidationMessage('password', false, '비밀번호는 최소 8자리여야 합니다.'); allValid = false; }
            else { setValidationMessage('password', true, '확인 완료'); }

            if (!validateConfirmPassword(password, confirmPassword)) { setValidationMessage('confirmPassword', false, '비밀번호가 일치하지 않습니다.'); allValid = false; }
            else { setValidationMessage('confirmPassword', true, '일치함'); }

            if (!validateEmail(email)) { setValidationMessage('email', false, '유효한 이메일 형식이 아닙니다.'); allValid = false; }
            else { setValidationMessage('email', true, '확인 완료'); }

            if (!allValid) return;

            const payload = {
                name,
                password,
                email,
                phoneNumber: userPhoneNumber,
                birthDate: userBirthDate,
                job: (userJob && userJob !== '선택...') ? userJob : null
            };

            const formBtn = document.getElementById('formBtn');
            if (formBtn) formBtn.disabled = true;

            try {
                // 이메일 인증 없이 바로 회원가입 요청
                await apiCall('/api/auth/register', 'POST', payload);
                alert('회원가입이 성공적으로 완료되었습니다.');
                window.location.href = '/auth/login';
            } catch (error) {
                alert('회원가입 실패: ' + (error.message || '오류 발생'));
            } finally {
                if (formBtn) formBtn.disabled = false;
            }
        });
    };
    handleRegister();

    // ============================================================
    // 4. 비밀번호 재설정 로직 (유지)
    // ============================================================
    const handlePasswordReset = () => {
        const resetPasswordForm = document.getElementById('resetPasswordForm');
        if (!resetPasswordForm) return;

        const nameInput = document.getElementById('name');
        const emailInput = document.getElementById('email');
        const newPwInput = document.getElementById('newPassword');
        const confirmPwInput = document.getElementById('confirmNewPassword');
        const resetBtn = resetPasswordForm.querySelector('button[type="submit"]');

        resetPasswordForm.addEventListener('submit', async function (event) {
            event.preventDefault();

            const name = nameInput.value.trim();
            const email = emailInput.value.trim();
            const newPassword = newPwInput.value;
            const confirmNewPassword = confirmPwInput.value;

            let allValid = true;
            // (유효성 검사 로직 생략 - 위와 동일)
            if (!validateName(name)) allValid = false;
            if (!validateEmail(email)) allValid = false;
            if (!validatePassword(newPassword)) allValid = false;
            if (!validateConfirmPassword(newPassword, confirmNewPassword)) allValid = false;

            if (!allValid) { alert('입력 정보를 확인해주세요.'); return; }

            if (resetBtn) { resetBtn.disabled = true; resetBtn.textContent = '처리 중...'; }

            try {
                await apiCall('/api/auth/password/reset', 'POST', { name, email, newPassword });
                alert('비밀번호가 성공적으로 변경되었습니다.');
                window.location.href = '/auth/password/reset/success';
            } catch (error) {
                alert('비밀번호 변경 실패: ' + (error.message || '오류 발생'));
            } finally {
                if (resetBtn) { resetBtn.disabled = false; resetBtn.textContent = '비밀번호 변경'; }
            }
        });
    };
    handlePasswordReset();
});