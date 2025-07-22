$(document).ready(function() { // 문서가 로드된 후 스크립트 실행
    $('#imageInput').on('change', function(event) {
        const file = this.files[0]; // jQuery에서는 'this'로 원본 DOM 요소에 접근

        if (file) {
            const reader = new FileReader();

            reader.onload = function(e) {
                const $previewDiv = $('#imagePreview'); // jQuery 객체로 가져오기
                $previewDiv.empty(); // 기존 내용 지우기

                const $img = $('<img>'); // jQuery 객체로 <img> 생성
                $img.attr('src', e.target.result); // src 속성 설정
                $img.attr('alt', '이미지 미리보기'); // alt 속성 설정

                $previewDiv.append($img); // 미리보기 영역에 이미지 추가
            };

            reader.readAsDataURL(file);
        } else {
            $('#imagePreview').html('<p>선택된 이미지가 여기에 표시됩니다.</p>'); // jQuery로 내용 설정
        }
    });
});