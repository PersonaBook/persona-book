// auth.js
document.addEventListener('DOMContentLoaded', function () {

    // ============================================================
    // 1. 로그인
    // ============================================================
    const handleLogin = () => {
        const loginForm = document.getElementById('loginForm');
        if (!loginForm) return;

        loginForm.addEventListener('submit', async function (event) {
            event.preventDefault();

            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const alertDiv = document.querySelector('.alert-danger');
            const alertP = alertDiv ? alertDiv.querySelector('p') : null;

            if (alertDiv) alertDiv.style.display = 'none';

            try {
                // 1. apiCall 호출 (ApiResponseDto.data인 AuthResponseDto 반환)
                const data = await apiCall('/api/auth/login', 'POST', { email, password });

                /**
                 * [응답 구조 데이터 매핑]
                 * data = {
                 * userId: 1,
                 * name: "홍길동",
                 * email: "test@test.com",
                 * token: {  <-- TokenDto 객체
                 * accessToken: "...",
                 * refreshToken: "..."
                 * }
                 * }
                 */

                // 2. 토큰 추출 (data.token 내부를 참조해야 함)
                if (data && data.token && data.token.accessToken) {
                    const accessToken = data.token.accessToken;
                    const refreshToken = data.token.refreshToken;

                    // 3. 로컬 스토리지 저장
                    localStorage.setItem('accessToken', accessToken);
                    if (refreshToken) {
                        localStorage.setItem('refreshToken', refreshToken);
                    }

                    console.log('로그인 성공: 토큰 저장 완료');

                    // 4. UI 갱신 및 페이지 이동
                    if (typeof HeaderAuthManager !== 'undefined') {
                        HeaderAuthManager.refresh();
                    }
                    window.location.href = '/';
                } else {
                    throw new Error('서버 응답 형식에 토큰 정보가 포함되어 있지 않습니다.');
                }

            } catch (error) {
                console.error('Login Error:', error);
                if (alertDiv && alertP) {
                    alertP.textContent = error.message;
                    alertDiv.style.display = 'block';
                } else {
                    handleApiError(error);
                }
            }
        });
    };
    handleLogin();

    // ============================================================
    // 2. 회원가입
    // ============================================================
    const handleRegister = () => {
        const joinForm = document.getElementById('registerForm');
        if (!joinForm) return;

        const emailInput = document.getElementById('email');
        const userBirthDateInput = document.getElementById('userBirthDate');

        // jQuery Datepicker 초기화 (필요 시)
        if (userBirthDateInput && typeof $ !== 'undefined' && typeof $.fn.datepicker === 'function') {
            $(userBirthDateInput).datepicker({
                maxDate: "-10y", changeMonth: true, changeYear: true, yearRange: "c-100:c", dateFormat: "yy-mm-dd"
            });
        }

        joinForm.addEventListener('submit', async function (event) {
            event.preventDefault();

            // 입력값 가져오기
            const name = document.getElementById('name').value;
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirmPassword').value;
            const email = emailInput.value;
            const userPhoneNumber = document.getElementById('userPhoneNumber').value;
            const userBirthDate = userBirthDateInput ? userBirthDateInput.value : '';
            const userJobSelect = document.getElementById('userJob');
            const userJob = (userJobSelect && userJobSelect.value !== '선택...') ? userJobSelect.value : null;

            // 유효성 검사
            let isValid = true;
            if (!validateName(name)) { setValidationMessage('name', false, '이름을 입력해주세요.'); isValid = false; }
            else setValidationMessage('name', true, '');

            if (!validateEmail(email)) { setValidationMessage('email', false, '올바른 이메일 형식이 아닙니다.'); isValid = false; }
            else setValidationMessage('email', true, '');

            if (!validatePassword(password)) { setValidationMessage('password', false, '8자 이상 입력해주세요.'); isValid = false; }
            else setValidationMessage('password', true, '');

            if (!validateConfirmPassword(password, confirmPassword)) { setValidationMessage('confirmPassword', false, '비밀번호가 일치하지 않습니다.'); isValid = false; }
            else setValidationMessage('confirmPassword', true, '');

            if (!isValid) return;

            const formBtn = document.getElementById('formBtn');
            if (formBtn) formBtn.disabled = true;

            const payload = { name, password, email, phoneNumber: userPhoneNumber, birthDate: userBirthDate, job: userJob };

            try {
                // Register는 ApiResponseDto.data가 null임. 성공 시 에러 안 나고 통과.
                await apiCall('/api/auth/register', 'POST', payload);
                alert('회원가입이 완료되었습니다.');
                window.location.href = '/auth/login';
            } catch (error) {
                // 이미 가입된 이메일 등 서버 에러 메시지 출력
                handleApiError(error);
            } finally {
                if (formBtn) formBtn.disabled = false;
            }
        });
    };
    handleRegister();

    // ============================================================
    // 3. 아이디 찾기
    // ============================================================
    const handleFindId = () => {
        const findIdForm = document.getElementById('findIdForm');
        if (!findIdForm) return;

        findIdForm.addEventListener('submit', async function (event) {
            event.preventDefault();
            const name = document.getElementById('name').value;
            const phoneNumber = document.getElementById('phoneNumber').value;

            if (!name || !phoneNumber) {
                alert('정보를 모두 입력해주세요.');
                return;
            }

            try {
                // 성공 시 data는 email(String)
                const foundEmail = await apiCall('/api/auth/id/find', 'POST', { name, phoneNumber });
                alert('아이디를 성공적으로 찾았습니다.');
                window.location.href = `/auth/id/find/success?email=${encodeURIComponent(foundEmail)}`;
            } catch (error) {
                handleApiError(error);
            }
        });
    };
    handleFindId();

    // ============================================================
    // 4. 비밀번호 재설정
    // ============================================================
    const handlePasswordReset = () => {
        const resetForm = document.getElementById('passwordResetForm');
        if (!resetForm) return;

        resetForm.addEventListener('submit', async function (event) {
            event.preventDefault();
            const name = document.getElementById('name').value;
            const email = document.getElementById('email').value;
            const newPassword = document.getElementById('newPassword').value;
            const confirmNewPassword = document.getElementById('confirmNewPassword').value;

            if (!validatePassword(newPassword)) { alert('비밀번호는 8자 이상이어야 합니다.'); return; }
            if (newPassword !== confirmNewPassword) { alert('비밀번호가 일치하지 않습니다.'); return; }

            try {
                await apiCall('/api/auth/password/reset', 'POST', { name, email, newPassword });
                alert('비밀번호가 성공적으로 변경되었습니다.');
                window.location.href = '/auth/password/reset/success';
            } catch (error) {
                handleApiError(error);
            }
        });
    };
    handlePasswordReset();
});