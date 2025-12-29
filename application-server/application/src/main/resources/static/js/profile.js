// profile.js

// --- User API ---
function getUserProfile() {
    return apiCall('/api/user/profile', 'GET');
}

function updateUserProfile(payload) {
    return apiCall('/api/user/profile', 'PATCH', payload);
}

document.addEventListener('DOMContentLoaded', function () {
    const profileForm = document.getElementById('profileForm');
    if (!profileForm) return;

    const cancelButton = document.getElementById('cancelButton');
    const errorDiv = document.getElementById('profile-error');

    // 폼의 모든 입력 필드를 채우는 함수
    function populateForm(user) {
        document.getElementById('name').value = user.name || '';
        document.getElementById('email').value = user.email || '';
        document.getElementById('birthDate').value = user.birthDate || '';
        document.getElementById('job').value = user.job || '';
        document.getElementById('phoneNumber').value = user.phoneNumber || '';
    }

    // 서버에서 사용자 프로필을 로드하는 함수
    async function loadUserProfile() {
        try {
            const userProfile = await getUserProfile();
            if (userProfile) {
                populateForm(userProfile);
                errorDiv.style.display = 'none';
            } else {
                throw new Error('프로필 정보를 가져오지 못했습니다.');
            }
        } catch (error) {
            // common.js의 전역 에러 핸들러가 401 등을 처리
            handleApiError(error);
        }
    }

    // --- 이벤트 리스너 설정 ---

    // 취소 버튼 클릭 시: 서버에서 데이터를 다시 로드하여 원상 복구
    cancelButton.addEventListener('click', function () {
        if (confirm('수정 중인 내용을 취소하시겠습니까?')) {
            loadUserProfile();
        }
    });

    // 폼 제출 시 (저장)
    profileForm.addEventListener('submit', async function (event) {
        event.preventDefault();

        const payload = {
            name: document.getElementById('name').value,
            // email은 수정하지 않으므로 페이로드에서 제외
            birthDate: document.getElementById('birthDate').value,
            job: document.getElementById('job').value,
            phoneNumber: document.getElementById('phoneNumber').value,
        };

        errorDiv.style.display = 'none';
        errorDiv.textContent = '';

        try {
            await updateUserProfile(payload);
            alert('프로필이 성공적으로 업데이트되었습니다.');
            await loadUserProfile(); // 성공 후 최신 데이터 다시 로드
        } catch (error) {
            errorDiv.textContent = error.message || '프로필 업데이트에 실패했습니다.';
            errorDiv.style.display = 'block';
        }
    });

    // --- 초기화 ---
    loadUserProfile(); // 페이지 로드 시 프로필 정보 로드
});
