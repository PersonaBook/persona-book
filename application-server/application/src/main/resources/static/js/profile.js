document.addEventListener('DOMContentLoaded', function () {
    console.log('profile.js: DOMContentLoaded event fired.');

    const profileForm = document.getElementById('profileForm');
    if (!profileForm) {
        console.log('profile.js: Profile form not found. Exiting.');
        return;
    }

    console.log('profile.js: Profile form found. Initializing event listeners.');

    const editButton = document.getElementById('editButton');
    const saveButton = document.getElementById('saveButton');
    const cancelButton = document.getElementById('cancelButton');
    const errorDiv = document.getElementById('profile-error');

    const inputs = profileForm.querySelectorAll('input');
    const originalValues = {};

    function setFormReadOnly(isReadOnly) {
        inputs.forEach(input => {
            if (isReadOnly) {
                input.setAttribute('readonly', true);
            } else {
                input.removeAttribute('readonly');
            }
        });

        editButton.style.display = isReadOnly ? 'inline-block' : 'none';
        saveButton.style.display = isReadOnly ? 'none' : 'inline-block';
        cancelButton.style.display = isReadOnly ? 'none' : 'inline-block';
    }

    editButton.addEventListener('click', function () {
        console.log('profile.js: Edit button clicked.');
        inputs.forEach(input => {
            originalValues[input.id] = input.value;
        });
        setFormReadOnly(false);
    });

    cancelButton.addEventListener('click', function () {
        console.log('profile.js: Cancel button clicked.');
        inputs.forEach(input => {
            input.value = originalValues[input.id];
        });
        setFormReadOnly(true);
        errorDiv.style.display = 'none';
    });

    profileForm.addEventListener('submit', async function (event) {
        event.preventDefault();
        console.log('profile.js: Profile form submitted.');
        
        const payload = {
            name: document.getElementById('name').value,
            email: document.getElementById('email').value,
            birthDate: document.getElementById('birthDate').value,
            job: document.getElementById('job').value,
            phoneNumber: document.getElementById('phoneNumber').value, // 추가
        };

        // Clear previous errors
        errorDiv.style.display = 'none';
        errorDiv.textContent = '';

        try {
            console.log('profile.js: Calling updateUserProfile API...');
            await updateUserProfile(payload);
            
            console.log('profile.js: Profile update successful.');
            setFormReadOnly(true);
            alert('프로필이 성공적으로 업데이트되었습니다.');
        } catch (error) {
            console.error('profile.js: Error during profile update API call:', error);
            let errorMessage = '프로필 업데이트에 실패했습니다.';
            if (error instanceof Error) {
                errorMessage = error.message;
            }
            errorDiv.textContent = errorMessage;
            errorDiv.style.display = 'block';
        }
    });
    setFormReadOnly(true); // 초기 상태는 읽기 전용
});
