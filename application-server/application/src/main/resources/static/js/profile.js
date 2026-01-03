// profile.js

// --- User API ---
function getUserProfile() {
    return apiCall('/api/user/profile', 'GET');
}

function updateUserProfile(payload) {
    return apiCall('/api/user/profile', 'PATCH', payload);
}

// --- Event Listeners ---
document.addEventListener('DOMContentLoaded', function () {
    initProfilePage();
});

/**
 * 프로필 페이지 초기화 및 이벤트 바인딩
 */
function initProfilePage() {
    const form = document.getElementById('profileForm');
    if (!form) return;
    
    const cancelButton = document.getElementById('cancelButton');

    // 1. 초기 데이터 로드
    loadUserProfile();

    // 2. 수정 취소 이벤트
    if (cancelButton) {
        cancelButton.addEventListener('click', function () {
            if (confirm('수정 중인 내용을 취소하시겠습니까?')) {
                loadUserProfile();
            }
        });
    }

    // 3. 프로필 저장(제출) 이벤트
    form.addEventListener('submit', async function (event) {
        event.preventDefault();
        await handleProfileUpdate();
    });
}

/**
 * 서버에서 프로필 데이터를 가져와 화면에 출력
 */
async function loadUserProfile() {
    const errorDiv = document.getElementById('profile-error');

    try {
        const userProfile = await getUserProfile();
        if (userProfile) {
            populateProfileForm(userProfile);
            if (errorDiv) errorDiv.style.display = 'none';
        } else {
            throw new Error('프로필 정보를 가져오지 못했습니다.');
        }
    } catch (error) {
        // common.js의 전역 에러 핸들러 활용
        handleApiError(error);
    }
}

/**
 * 프로필 업데이트 처리
 */
async function handleProfileUpdate() {
    const errorDiv = document.getElementById('profile-error');
    const payload = {
        name: document.getElementById('name').value,
        birthDate: document.getElementById('birthDate').value,
        job: document.getElementById('job').value,
        phoneNumber: document.getElementById('phoneNumber').value,
    };

    if (errorDiv) {
        errorDiv.style.display = 'none';
        errorDiv.textContent = '';
    }

    try {
        await updateUserProfile(payload);
        alert('프로필이 성공적으로 업데이트되었습니다.');
        await loadUserProfile(); // 최신 데이터로 폼 갱신
    } catch (error) {
        if (errorDiv) {
            errorDiv.textContent = error.message || '프로필 업데이트에 실패했습니다.';
            errorDiv.style.display = 'block';
        } else {
            handleApiError(error);
        }
    }
}

/**
 * 폼 입력 필드에 데이터 바인딩 (Helper)
 */
function populateProfileForm(user) {
    const fields = ['name', 'email', 'birthDate', 'job', 'phoneNumber'];
    fields.forEach(field => {
        const element = document.getElementById(field);
        if (element) {
            element.value = user[field] || '';
        }
    });
}