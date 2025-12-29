// 이 파일은 사용자 인증(로그인, 회원가입, 아이디 찾기, 비밀번호 재설정 등)과 관련된 모든 클라이언트 사이드 로직을 담당합니다.
// 각 인증 플로우에 대한 폼 제출 처리, API 호출, 유효성 검사, 그리고 결과에 따른 UI 업데이트 및 페이지 리다이렉션을 포함합니다.

document.addEventListener('DOMContentLoaded', function () {
    console.log('auth.js: DOMContentLoaded event fired.');

    // --- 공통 유틸리티 함수 ---
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

    // --- 유효성 검사 함수 ---
    function validateEmail(email) {
        const re = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        return re.test(String(email).toLowerCase());
    }

    function validateName(name) {
        return name.trim().length > 0;
    }

    function validatePassword(password) {
        return password.length >= 8; // 최소 8자리
    }

    function validateConfirmPassword(password, confirmPassword) {
        return password === confirmPassword;
    }

    // --- 로그인 로직 ---
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        console.log('auth.js: Login form found. Binding event listener.');
        loginForm.addEventListener('submit', async function (event) {
            event.preventDefault();
            console.log('auth.js: Login form submitted.');
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const alertDiv = document.querySelector('#loginForm .alert-danger'); // loginForm 내의 alert
            const alertParagraph = alertDiv ? alertDiv.querySelector('p') : null;

            if (alertDiv) alertDiv.style.display = 'none';

            try {
                console.log('auth.js: Calling /api/auth/login...');
                const responseData = await apiCall('/api/auth/login', 'POST', { email: email, password: password });
                
                if (responseData && responseData.token && responseData.token.accessToken && responseData.token.refreshToken) {
                    console.log('auth.js: Login successful. Storing tokens.');
                    const { accessToken, refreshToken } = responseData.token;
                    localStorage.setItem('accessToken', accessToken);
                    localStorage.setItem('refreshToken', refreshToken);

                    if (typeof HeaderAuthManager !== 'undefined') {
                        console.log('auth.js: Refreshing HeaderAuthManager.');
                        HeaderAuthManager.refresh();
                    }
                    
                    console.log('auth.js: Redirecting to homepage.');
                    window.location.href = '/'; // Redirect to homepage
                } else if (responseData && responseData.token) {
                    console.error('auth.js: Login failed: token object missing accessToken or refreshToken.');
                    if (alertParagraph) alertParagraph.textContent = '로그인 처리 중 필수 토큰 정보가 누락되었습니다.';
                    if (alertDiv) alertDiv.style.display = 'block';
                } else {
                    console.error('auth.js: Login failed: no token in responseData.');
                    if (alertParagraph) alertParagraph.textContent = '로그인 처리 중 예상치 못한 오류가 발생했습니다.';
                    if (alertDiv) alertDiv.style.display = 'block';
                }
            } catch (error) {
                console.error('auth.js: Error during login API call:', error);
                let errorMessage = '로그인에 실패했습니다.';
                if (error instanceof Error) {
                    errorMessage = error.message;
                }
                if (alertParagraph) alertParagraph.textContent = errorMessage;
                if (alertDiv) alertDiv.style.display = 'block';
            }
        });
    }

    // --- 회원가입 로직 (register.js 내용 통합) ---
    const joinForm = document.getElementById('join_area');
    if (joinForm) {
        const sendVerificationCodeBtn = document.getElementById('sendVerificationCodeBtn');
        const verifyCodeBtn = document.getElementById('verifyCodeBtn');
        const verificationCodeSection = document.getElementById('verificationCodeSection');
        const emailInput = document.getElementById('email');
        const verificationCodeInput = document.getElementById('verificationCode');
        const codeVerificationMessage = document.getElementById('codeVerificationMessage');
        const userBirthDateInput = document.getElementById('userBirthDate'); // Datepicker를 위한 필드

        // jQuery UI Datepicker 초기화
        if (typeof $ !== 'undefined' && typeof $.fn.datepicker === 'function') {
            $(userBirthDateInput).datepicker({
                maxDate: "-10y",
                changeMonth: true,
                changeYear: true,
                yearRange: "c-100:c",
                dateFormat: "yy-mm-dd"
            });
        }


        // 인증번호 발송
        if (sendVerificationCodeBtn) {
            sendVerificationCodeBtn.addEventListener('click', async function () {
                const email = emailInput.value;
                if (!validateEmail(email)) {
                    setValidationMessage('email', false, '유효한 이메일 주소를 입력해주세요.');
                    return;
                }

                this.disabled = true;
                try {
                    await apiCall('/api/email/send/code', 'POST', {email: email});
                    alert('인증번호가 발송되었습니다. 이메일을 확인해주세요.');
                    verificationCodeSection.style.display = 'block';
                    setValidationMessage('email', true, '인증번호 발송 완료');
                } catch (error) {
                    alert('인증번호 발송 실패: ' + (error.message || '알 수 없는 오류'));
                    setValidationMessage('email', false, error.message || '인증번호 발송 실패');
                } finally {
                    this.disabled = false;
                }
            });
        }

        // 인증번호 확인
        if (verifyCodeBtn) {
            verifyCodeBtn.addEventListener('click', async function () {
                const email = emailInput.value;
                const code = verificationCodeInput.value;

                if (!code.trim()) {
                    codeVerificationMessage.textContent = '인증번호를 입력해주세요.';
                    codeVerificationMessage.style.color = 'red';
                    return;
                }

                this.disabled = true;
                try {
                    await apiCall('/api/email/verification', 'POST', {email: email, code: code});
                    codeVerificationMessage.textContent = '이메일 인증에 성공했습니다.';
                    codeVerificationMessage.style.color = 'green';
                    emailInput.readOnly = true;
                    if (sendVerificationCodeBtn) sendVerificationCodeBtn.disabled = true;
                } catch (error) {
                    codeVerificationMessage.textContent = '인증번호 확인 실패: ' + (error.message || '알 수 없는 오류');
                    codeVerificationMessage.style.color = 'red';
                } finally {
                    this.disabled = false;
                }
            });
        }

        // 회원가입 폼 제출
        joinForm.addEventListener('submit', async function (event) {
            event.preventDefault();

            const name = document.getElementById('name').value;
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirmPassword').value;
            const email = emailInput.value;
            const userPhoneNumber = document.getElementById('userPhoneNumber').value;
            const userBirthDate = userBirthDateInput.value;
            const userJob = document.getElementById('userJob').value;

            let allValid = true;
            if (!validateName(name)) { setValidationMessage('name', false, '이름을 입력해주세요.'); allValid = false; } else { setValidationMessage('name', true, '이름 확인 완료.'); }
            if (!validatePassword(password)) { setValidationMessage('password', false, '비밀번호는 최소 8자리여야 합니다.'); allValid = false; } else { setValidationMessage('password', true, '비밀번호 확인 완료.'); }
            if (!validateConfirmPassword(password, confirmPassword)) { setValidationMessage('confirmPassword', false, '비밀번호가 일치하지 않습니다.'); allValid = false; } else { setValidationMessage('confirmPassword', true, '비밀번호 일치 확인 완료.'); }
            
            if (!allValid) { alert('입력 정보를 다시 확인해주세요.'); return; }

            const payload = {
                name: name,
                password: password,
                email: email,
                phoneNumber: userPhoneNumber,
                birthDate: userBirthDate,
                job: userJob !== '선택...' ? userJob : null
            };

            const formBtn = document.getElementById('formBtn');
            formBtn.disabled = true;

            try {
                await apiCall('/api/auth/register', 'POST', payload);
                alert('회원가입이 성공적으로 완료되었습니다.');
                window.location.href = '/auth/login';
            } catch (error) {
                alert('회원가입 실패: ' + (error.message || '알 수 없는 오류'));
            } finally {
                formBtn.disabled = false;
            }
        });
    }

        // --- 비밀번호 재설정 로직 (password-reset.html) ---

        const resetPasswordForm = document.getElementById('resetPasswordForm');

        if (resetPasswordForm) {

            console.log('auth.js: Reset Password form found. Binding event listeners.');

            const resetPasswordNameInput = document.getElementById('name');

            const resetPasswordEmailInput = document.getElementById('email');

            const newPasswordInput = document.getElementById('newPassword');

            const confirmNewPasswordInput = document.getElementById('confirmNewPassword');

            const resetFormBtn = document.querySelector('#resetPasswordForm button[type="submit"]');

    

            resetPasswordForm.addEventListener('submit', async function (event) {

                event.preventDefault();

                console.log('auth.js: Reset Password form submitted.');

    

                const name = resetPasswordNameInput.value.trim();

                const email = resetPasswordEmailInput.value.trim();

                const newPassword = newPasswordInput.value;

                const confirmNewPassword = confirmNewPasswordInput.value;

    

                let allValid = true;

    

                if (!validateName(name)) { setValidationMessage('name', false, '이름을 입력해주세요.'); allValid = false; } else { setValidationMessage('name', true, ''); }

                if (!validateEmail(email)) { setValidationMessage('email', false, '유효한 이메일 주소를 입력해주세요.'); allValid = false; } else { setValidationMessage('email', true, ''); }

                if (!validatePassword(newPassword)) { setValidationMessage('newPassword', false, '비밀번호는 최소 8자리여야 합니다.'); allValid = false; } else { setValidationMessage('newPassword', true, '비밀번호 확인 완료.'); }

                if (!validateConfirmPassword(newPassword, confirmNewPassword)) { setValidationMessage('confirmNewPassword', false, '비밀번호가 일치하지 않습니다.'); allValid = false; } else { setValidationMessage('confirmNewPassword', true, '비밀번호 일치 확인 완료.'); }

    

                if (!allValid) {

                    alert('입력 정보를 다시 확인해주세요.');

                    return;

                }

    

                resetFormBtn.disabled = true;

                resetFormBtn.textContent = '처리 중...';

    

                const payload = {

                    name: name,

                    email: email,

                    newPassword: newPassword

                };

    

                try {

                    console.log('auth.js: Reset Password: Calling /api/auth/password/reset...');

                    await apiCall('/api/auth/password/reset', 'POST', payload);

                    alert('비밀번호가 성공적으로 변경되었습니다.');

                    window.location.href = '/auth/password/reset/success';

                } catch (error) {

                    console.error('auth.js: Reset Password: Error during password reset API call:', error);

                    alert('비밀번호 변경 실패: ' + (error.message || '알 수 없는 오류'));

                } finally {

                    resetFormBtn.disabled = false;

                    resetFormBtn.textContent = '비밀번호 변경';

                }

            });

        } else {

            console.log('auth.js: Reset Password form not found.');

        } else {
        console.log('auth.js: Reset Password form not found.');
    }
});
