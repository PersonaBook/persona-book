// 검증 메시지
const LOGIN_MESSAGES = {
    EMAIL: {
        invalid: '올바른 이메일 형식을 입력해주세요.',
        valid: '올바른 이메일 형식입니다.',
        required: '이메일은 필수 입력 항목입니다.'
    },
    PASSWORD: {
        invalid: '비밀번호는 영문자, 숫자, 특수문자(!@#$%^&*)를 포함하여 8-20자여야 합니다.',
        valid: '사용 가능한 비밀번호입니다.',
        required: '비밀번호는 필수 입력 항목입니다.'
    },
    CONFIRM_PASSWORD: {
        invalid: '비밀번호가 일치하지 않습니다.',
        valid: '비밀번호가 일치합니다.',
        required: '비밀번호 확인은 필수 입력 항목입니다.'
    },
    NAME: {
        invalid: '이름은 한글만 사용 가능하며 2-10자여야 합니다.',
        valid: '올바른 이름입니다.',
        required: '이름은 필수 입력 항목입니다.'
    },
    VERIFICATION_CODE: {
        required: '인증번호를 입력해주세요.',
        invalid: '인증번호가 일치하지 않습니다.',
        valid: '인증번호가 확인되었습니다.'
    }
};

const loginValidationState = {
    email: false,
    password: false,
    confirmPassword: false,
    name: false,
    isEmailVerified: false
};

/**
 * 유효성 검사 결과를 UI에 표시하는 함수
 */
function displayValidationResult(elementId, isValid, message) {
    const $input = $('#' + elementId);
    const $errorFeedback = $('#' + elementId + 'Error');
    const $successFeedback = $('#' + elementId + 'Success');

    if ($input.length === 0 || $errorFeedback.length === 0 || $successFeedback.length === 0) {
        console.warn(`Validation elements for ${elementId} not found.`);
        return;
    }

    $input.removeClass('is-invalid is-valid');

    if (isValid) {
        $input.addClass('is-valid');
        $errorFeedback.hide().text('');
        $successFeedback.text(message).show();
    } else {
        $input.addClass('is-invalid');
        $successFeedback.hide().text('');
        $errorFeedback.text(message).show();
    }
}

/**
 * 인증번호 관련 메시지를 UI에 표시하는 함수
 */
function displayVerificationMessage($element, message, color) {
    if ($element.length > 0) {
        $element.text(message).css('color', color);
    }
}

/**
 * 로그인 버튼 활성화/비활성화
 */
// function updateLoginButton() {
//     const $formBtn = $('#form_area button[type="submit"]');
//     if ($formBtn.length > 0) {
//         // Checks if ALL values in loginValidationState are true
//         const allFieldsValid = Object.values(loginValidationState).every(isValid => isValid);
//         // Sets the 'disabled' property of the button
//         $formBtn.prop('disabled', !allFieldsValid);
//     }
// }

/**
 * 이메일 유효성 검사
 */
function validateEmail() {
    // 패턴을 함수 내부로 이동
    const EMAIL_PATTERN = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

    const $emailInput = $('#email');
    if ($emailInput.length === 0) return false;

    const email = $emailInput.val().trim();
    let isValid = true;
    let message = '';

    if (email.length === 0) {
        isValid = false;
        message = LOGIN_MESSAGES.EMAIL.required;
    } else if (!EMAIL_PATTERN.test(email)) {
        isValid = false;
        message = LOGIN_MESSAGES.EMAIL.invalid;
    } else {
        message = LOGIN_MESSAGES.EMAIL.valid;
    }

    displayValidationResult('email', isValid, message);
    loginValidationState.email = isValid;

    if (loginValidationState.isEmailVerified && !isValid) {
        loginValidationState.isEmailVerified = false;
        displayVerificationMessage($('#codeVerificationMessage'), '', '');
    }
    // updateLoginButton();
    return isValid;
}

/**
 * 비밀번호 유효성 검사
 */
function validatePassword() {
    // 패턴을 함수 내부로 이동
    const PASSWORD_PATTERN = /^(?=.*[a-zA-Z])(?=.*[0-9])(?=.*[!@#$%^&*])[a-zA-Z0-9!@#$%^&*]{8,20}$/;

    const $passwordInput = $('#password');
    if ($passwordInput.length === 0) return false;

    const password = $passwordInput.val();
    let isValid = true;
    let message = '';

    if (password.length === 0) {
        isValid = false;
        message = LOGIN_MESSAGES.PASSWORD.required;
    } else if (!PASSWORD_PATTERN.test(password)) {
        isValid = false;
        message = LOGIN_MESSAGES.PASSWORD.invalid;
    } else {
        message = LOGIN_MESSAGES.PASSWORD.valid;
    }

    displayValidationResult('password', isValid, message);
    loginValidationState.password = isValid;
    // updateLoginButton();
    return isValid;
}

/**
 * 이름 유효성 검사
 */
function validateName() {
    // 패턴을 함수 내부로 이동
    const NAME_PATTERN = /^[가-힣]{2,10}$/;

    const $nameInput = $('#name');
    if ($nameInput.length === 0) return false;

    const name = $nameInput.val().trim();
    let isValid = true;
    let message = '';

    if (name.length === 0) {
        isValid = false;
        message = LOGIN_MESSAGES.NAME.required;
    } else if (!NAME_PATTERN.test(name)) {
        isValid = false;
        message = LOGIN_MESSAGES.NAME.invalid;
    } else {
        message = LOGIN_MESSAGES.NAME.valid;
    }

    displayValidationResult('name', isValid, message);
    loginValidationState.name = isValid;
    // updateLoginButton();
    return isValid;
}

/**
 * 비밀번호 확인 유효성 검사
 */
function validateConfirmPassword() {
    const $passwordInput = $('#password');
    const $confirmPasswordInput = $('#confirmPassword');
    if ($passwordInput.length === 0 || $confirmPasswordInput.length === 0) return false;

    const password = $passwordInput.val();
    const confirmPassword = $confirmPasswordInput.val();
    let isValid = true;
    let message = '';

    if (confirmPassword.length === 0) {
        isValid = false;
        message = LOGIN_MESSAGES.CONFIRM_PASSWORD.required;
    } else if (password !== confirmPassword) {
        isValid = false;
        message = LOGIN_MESSAGES.CONFIRM_PASSWORD.invalid;
    } else {
        message = LOGIN_MESSAGES.CONFIRM_PASSWORD.valid;
    }

    displayValidationResult('confirmPassword', isValid, message);
    loginValidationState.confirmPassword = isValid;
    // updateLoginButton();
    return isValid;
}


/**
 * 실시간 유효성 검사 초기화
 */
function initializeLoginValidation() {
    const $emailInput = $('#email');
    const $passwordInput = $('#password');
    const $confirmPasswordInput = $('#confirmPassword');
    const $nameInput = $('#name');
    const $userPhoneNumberInput = $('#userPhoneNumber');
    const form = $('form');
    form.attr('id', 'form_area'); // form에 ID가 없으므로 동적으로 추가

    const $sendVerificationCodeBtn = $('#sendVerificationCodeBtn');
    const $verificationCodeSection = $('#verificationCodeSection');
    const $verifyCodeBtn = $('#verifyCodeBtn');
    const $verificationCodeInput = $('#verificationCode');
    const $codeVerificationMessageDiv = $('#codeVerificationMessage');

    const $userBirthDateInput = $('#userBirthDate'); // 생년월일 input 추가
    const $userJobSelect = $('#userJob');
    const $otherJobContainer = $('#other-job-container');

    console.log('로그인 유효성 검사 초기화 시작');

    // 이메일 필드 이벤트 리스너
    if ($emailInput.length > 0) {
        console.log('이메일 필드 이벤트 리스너 추가');
        $emailInput.on('input', function() {
            console.log('이메일 input 이벤트 발생:', $(this).val());
            validateEmail();
        }).on('blur', function() {
            console.log('이메일 blur 이벤트 발생:', $(this).val());
            validateEmail();
        }).on('focus', function() {
            if ($(this).val().trim() === '') {
                $(this).removeClass('is-invalid is-valid');
                $('#emailError').hide().text('');
                $('#emailSuccess').hide().text('');
            }
        });
    }

    // 비밀번호 필드 이벤트 리스너
    if ($passwordInput.length > 0) {
        console.log('비밀번호 필드 이벤트 리스너 추가');
        $passwordInput.on('input', function() {
            console.log('비밀번호 input 이벤트 발생');
            validatePassword();
            if ($confirmPasswordInput.length > 0) {
                validateConfirmPassword();
            }
        }).on('blur', function() {
            console.log('비밀번호 blur 이벤트 발생');
            validatePassword();
            if ($confirmPasswordInput.length > 0) {
                validateConfirmPassword();
            }
        }).on('focus', function() {
            if ($(this).val().trim() === '') {
                $(this).removeClass('is-invalid is-valid');
                $('#passwordError').hide().text('');
                $('#passwordSuccess').hide().text('');
            }
        });
    }

    // 비밀번호 재확인 필드 이벤트 리스너
    if ($confirmPasswordInput.length > 0) {
        console.log('비밀번호 재확인 필드 이벤트 리스너 추가');
        $confirmPasswordInput.on('input', function() {
            console.log('비밀번호 재확인 input 이벤트 발생');
            validateConfirmPassword();
        }).on('blur', function() {
            console.log('비밀번호 재확인 blur 이벤트 발생');
            validateConfirmPassword();
        }).on('focus', function() {
            if ($(this).val().trim() === '') {
                $(this).removeClass('is-invalid is-valid');
                $('#confirmPasswordError').hide().text('');
                $('#confirmPasswordSuccess').hide().text('');
            }
        });
    }

    // 이름 필드 이벤트 리스너
    if ($nameInput.length > 0) {
        console.log('이름 필드 이벤트 리스너 추가');
        $nameInput.on('input', function() {
            console.log('이름 input 이벤트 발생');
            validateName();
        }).on('blur', function() {
            console.log('이름 blur 이벤트 발생');
            validateName();
        }).on('focus', function() {
            if ($(this).val().trim() === '') {
                $(this).removeClass('is-invalid is-valid');
                $('#nameError').hide().text('');
                $('#nameSuccess').hide().text('');
            }
        });
    }

    // 전화번호 필드 자동 하이픈 추가
    if ($userPhoneNumberInput.length > 0) {
        console.log('전화번호 필드 이벤트 리스너 추가');
        $userPhoneNumberInput.on('input', function(event) {
            let phoneNumber = $(this).val().replace(/[^0-9]/g, ''); // 숫자만 남기기
            let formattedPhoneNumber = '';

            if (phoneNumber.length > 0) {
                if (phoneNumber.length < 4) {
                    formattedPhoneNumber = phoneNumber;
                } else if (phoneNumber.length < 8) {
                    formattedPhoneNumber = phoneNumber.substring(0, 3) + '-' + phoneNumber.substring(3);
                } else if (phoneNumber.length < 12) { // 11자리까지 입력 가능 (010-1234-5678)
                    formattedPhoneNumber = phoneNumber.substring(0, 3) + '-' + phoneNumber.substring(3, 7) + '-' + phoneNumber.substring(7);
                } else { // 11자리를 초과하면 11자리까지만 허용
                    formattedPhoneNumber = phoneNumber.substring(0, 3) + '-' + phoneNumber.substring(3, 7) + '-' + phoneNumber.substring(7, 11);
                }
            }
            $(this).val(formattedPhoneNumber);
        });
    }

    // 직업 선택 시 '기타' 선택하면 '직접입력' 필드 보이게/숨기게
    if ($userJobSelect.length > 0 && $otherJobContainer.length > 0) {
        console.log('직업 선택 이벤트 리스너 추가');
        $userJobSelect.on('change', function() {
            if ($(this).val() === 'other') {
                $otherJobContainer.show();
            } else {
                $otherJobContainer.hide();
            }
        });
    }

    // 인증번호 발송 버튼 이벤트 리스너 추가
    if ($sendVerificationCodeBtn.length > 0 && $verificationCodeSection.length > 0) {
        $sendVerificationCodeBtn.on('click', function() {
            console.log('인증번호 발송 버튼 클릭됨');
            const isEmailValid = validateEmail();

            if (isEmailValid) {
                $verificationCodeSection.show();

                const email = $emailInput.val();
                $.ajax({
                    url: '/api/auth/sendVerificationEmail',
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify({ email: email }),
                    success: function(data) {
                        displayVerificationMessage($codeVerificationMessageDiv, data.message || '인증번호를 발송했습니다.', 'green');
                        loginValidationState.isEmailVerified = false;
                        // updateLoginButton();
                    },
                    error: function(jqXHR) {
                        console.error('Error sending verification email:', jqXHR.responseText);
                        const errorMessage = jqXHR.responseJSON ? jqXHR.responseJSON.message : '인증번호 발송 중 오류가 발생했습니다.';
                        displayVerificationMessage($codeVerificationMessageDiv, '오류: ' + errorMessage, 'red');
                    }
                });
            } else {
                alert(LOGIN_MESSAGES.EMAIL.invalid);
            }
        });
    }

    // 인증번호 확인 버튼 이벤트 리스너
    if ($verifyCodeBtn.length > 0 && $verificationCodeInput.length > 0) {
        $verifyCodeBtn.on('click', function() {
            console.log('인증번호 확인 버튼 클릭됨');
            const email = $emailInput.val().trim();
            const code = $verificationCodeInput.val().trim();

            if (code.length === 0) {
                displayVerificationMessage($codeVerificationMessageDiv, LOGIN_MESSAGES.VERIFICATION_CODE.required, 'red');
                loginValidationState.isEmailVerified = false;
                // updateLoginButton();
                return;
            }

            $.ajax({
                url: '/api/auth/verifyEmail',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ email: email, code: code }),
                success: function(data) {
                    displayVerificationMessage($codeVerificationMessageDiv, data.message || LOGIN_MESSAGES.VERIFICATION_CODE.valid, 'green');
                    loginValidationState.isEmailVerified = true;
                    // updateLoginButton();
                },
                error: function(jqXHR) {
                    console.error('Error verifying email code:', jqXHR.responseText);
                    const errorMessage = jqXHR.responseJSON ? jqXHR.responseJSON.message : LOGIN_MESSAGES.VERIFICATION_CODE.invalid;
                    displayVerificationMessage($codeVerificationMessageDiv, '오류: ' + errorMessage, 'red');
                    loginValidationState.isEmailVerified = false;
                    // updateLoginButton();
                }
            });
        });
    }

    // 폼 제출 이벤트
    if (form.length > 0) {
        form.on('submit', function(event) {
            console.log('폼 제출 시도');

            const isEmailValid = validateEmail();
            const isPasswordValid = validatePassword();
            const isConfirmPasswordValid = validateConfirmPassword();
            const isNameValid = validateName();
            const isEmailVerified = loginValidationState.isEmailVerified;

            // 추가: 생년월일이 비어있으면 경고
            const userBirthDate = $userBirthDateInput.val().trim();
            if (userBirthDate.length === 0) {
                alert('생년월일을 입력해주세요.');
                event.preventDefault();
                return false;
            }

            if (!isEmailValid || !isPasswordValid || !isConfirmPasswordValid || !isNameValid || !isEmailVerified) {
                event.preventDefault();
                let alertMessage = '입력 정보를 확인해주세요.';
                if (!isEmailVerified) {
                    alertMessage += '\n이메일 인증을 완료해주세요.';
                }
                alert(alertMessage);
                return false;
            }

            console.log('폼 제출 허용');
        });
    }

    // 초기 버튼 상태 설정
    // updateLoginButton();

    console.log('로그인 유효성 검사 초기화 완료');
}

// DOM이 로드된 후 초기화
$(document).ready(function() {
    console.log('DOM 로드 완료, 초기화 시작');
    if (typeof window.loginValidationInitialized === 'undefined' || !window.loginValidationInitialized) {
        initializeLoginValidation();
        window.loginValidationInitialized = true;
    }
});