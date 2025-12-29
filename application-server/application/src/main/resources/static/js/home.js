$(document).ready(function () {
    console.log('main/script.js 실행');

    // PDF.js worker 소스 설정
    pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.16.105/pdf.worker.min.js';

    if (getAuthToken()) {
        loadPdfList();
    } else {
        $("#imageInput").removeAttr('accept');
        $("#imageInput").removeAttr("type");
        $("#imageInput").off('click').on('click', function () { // .off('click') 추가하여 이전 이벤트 리스너 제거
            alert("로그인 또는 회원가입을 해주세요.")
        });
    }

    $('#imageInput').on('change', function (event) {
        const file = this.files[0];
        const $originalPlusArea = $(this).closest('.pdf_contents > li');

        if (file) {
            if (file.type === "application/pdf") {
                if (typeof pdfjsLib === 'undefined') {
                    alert("PDF.js 라이브러리가 로드되지 않아 PDF를 미리 볼 수 없습니다.");
                    $originalPlusArea.find('#imagePreview').html('<p style="color: red;">PDF.js 라이브러리 로드 오류.</p>');
                    $(this).val('');
                    return;
                }

                const reader = new FileReader();

                reader.onload = function (e) {
                    const pdfData = e.target.result;

                    const uint8Array = new Uint8Array(pdfData);
                    let binaryString = '';
                    const chunkSize = 8192;
                    for (let i = 0; i < uint8Array.length; i += chunkSize) {
                        const chunk = uint8Array.slice(i, i + chunkSize);
                        binaryString += String.fromCharCode.apply(null, chunk);
                    }
                    const pdfBase64 = btoa(binaryString);

                    const loadingTask = pdfjsLib.getDocument({data: pdfData});
                    loadingTask.promise.then(function (pdf) {
                        pdf.getPage(1).then(function (page) {
                            const $newPlusArea = $originalPlusArea.clone();
                            $newPlusArea.find('#imageInput').remove();
                            $newPlusArea.find('label.custom_file_button').remove();
                            $newPlusArea.find('#imagePreview').remove();
                            $newPlusArea.addClass("pdf_li");

                            const $newFileArea = $newPlusArea.find('.file_area');
                            $newFileArea.empty();
                            $newFileArea.css("z-index", "1");
                            const scale = 1.1;
                            const viewport = page.getViewport({scale: scale});

                            const $canvas = $('<canvas></canvas>');
                            $canvas.css({
                                'max-width': '100%',
                                'height': '100%',
                                'display': 'block',
                                'margin': 'auto'
                            });
                            $newFileArea.append($canvas);

                            const canvas = $canvas[0];
                            const context = canvas.getContext('2d');

                            canvas.height = viewport.height;
                            canvas.width = viewport.width;

                            const renderContext = {
                                canvasContext: context,
                                viewport: viewport
                            };
                            page.render(renderContext).promise.then(function () {
                                console.log('PDF rendered on new canvas!');
                                uploadPdfToServer(file.name, pdfBase64, $newPlusArea);
                            });

                            $originalPlusArea.before($newPlusArea);

                            $originalPlusArea.find('#imagePreview').html('<p></p>');
                            $(event.target).val('');

                        }).catch(function (error) {
                            console.error('Error getting PDF page:', error);
                            $originalPlusArea.find('#imagePreview').html('<p style="color: red;">PDF 페이지 로드 실패.</p>');
                        });
                    }).catch(function (error) {
                        console.error('Error loading PDF document:', error);
                        $originalPlusArea.find('#imagePreview').html('<p style="color: red;">PDF 문서 로드 실패.</p>');
                    });
                };

                reader.readAsArrayBuffer(file);
            } else if (file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    const $currentPreviewDiv = $originalPlusArea.find('#imagePreview');
                    $currentPreviewDiv.empty();
                    const $img = $('<img>');
                    $img.attr('src', e.target.result);
                    $img.attr('alt', '이미지 미리보기');
                    $img.css({
                        'max-width': '100%',
                        'max-height': '100%',
                        'object-fit': 'cover',
                        'display': 'block',
                        'margin': 'auto'
                    });
                    $currentPreviewDiv.append($img);
                };
                reader.readAsDataURL(file);
            } else {
                $originalPlusArea.find('#imagePreview').html('<p style="color: red;">지원하지 않는 파일 형식입니다. </br>(PDF 또는 이미지)</p>');
                $(this).val('');
            }
        } else {
            $originalPlusArea.find('#imagePreview').html('<p></p>');
        }
    });
});

function loadPdfList() {
    apiCall('/api/book/list', 'GET')
        .then(response => {
            if (Array.isArray(response)) {
                displayPdfList(response);
            }
        })
        .catch(error => {
            console.error('PDF 목록 로드 실패:', error);
            // apiCall 내부에서 handleApiError가 호출되므로 여기서는 추가적인 에러 UI 처리를 하지 않습니다.
            // 다만, 목록 로딩 실패 시 사용자에게 보여줄 메시지 등이 필요하다면 추가할 수 있습니다.
        });
}

function displayPdfList(pdfList) {
    const $pdfContents = $('.pdf_contents');
    const $originalPlusArea = $pdfContents.find('li:last-child');

    pdfList.forEach(function (pdf) {
        const $pdfItem = $('<li class="pdf_li"></li>');
        $pdfItem.html(`
                <div class="file_area" style="cursor: pointer;">
                    <img src="http://localhost:8000/api/v1/pdf-first-page/${pdf.bookId}"
                         alt="${pdf.title}"
                         style="max-width: 100%; height: 100%; display: block; margin: auto; object-fit: contain;"
                         onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22200%22 height=%22200%22%3E%3Crect width=%22200%22 height=%22200%22 fill=%22%23f0f0f0%22/%3E%3Ctext x=%2250%25%22 y=%2250%25%22 dominant-baseline=%22middle%22 text-anchor=%22middle%22 fill=%22%23999%22%3EPDF%3C/text%3E%3C/svg%3E';">
                </div>
                <div class="pdf_title" onclick="goToPdfDetail(${pdf.bookId});">
                    ${pdf.title}
                </div>
        `);

        $originalPlusArea.before($pdfItem);
    });
}

function renderPdfPreview(base64Data, canvas) {
    try {
        const binaryString = atob(base64Data);
        const bytes = new Uint8Array(binaryString.length);
        for (let i = 0; i < binaryString.length; i++) {
            bytes[i] = binaryString.charCodeAt(i);
        }

        const loadingTask = pdfjsLib.getDocument({data: bytes});
        loadingTask.promise.then(function (pdf) {
            pdf.getPage(1).then(function (page) {
                const scale = 1.1;
                const viewport = page.getViewport({scale: scale});
                const context = canvas.getContext('2d');

                canvas.height = viewport.height;
                canvas.width = viewport.width;

                const renderContext = {
                    canvasContext: context,
                    viewport: viewport
                };

                page.render(renderContext);
            });
        });
    } catch (error) {
        console.error('PDF 미리보기 렌더링 실패:', error);
    }
}

function uploadPdfToServer(title, fileBase64, $pdfElement) {
    const payload = {
        title: title,
        file_base64: fileBase64
    };

    apiCall('/api/book/upload', 'POST', payload)
        .then(response => {
            console.log('PDF 업로드 성공:', response);
            if (response && response.bookId) { // apiCall은 response.data를 직접 반환하므로 response에 bookId가 있을 것으로 예상
                $pdfElement.append(`<div class="pdf_title">${title}</div>`);
                $pdfElement.find('.pdf_title').attr('onclick', `goToPdfDetail(${response.bookId})`);
                window.location.reload();
            } else {
                alert('PDF 업로드 성공했지만 bookId를 찾을 수 없습니다.');
                $pdfElement.remove();
            }
        })
        .catch(error => {
            console.error('PDF 업로드 실패:', error);
            // apiCall 내부에서 handleApiError가 호출되므로 여기서는 추가적인 에러 UI 처리를 하지 않습니다.
            alert('PDF 업로드 실패: ' + (error.message || '알 수 없는 오류'));
            $pdfElement.remove();
        });
}

function goToPdfDetail(bookId) {
    const token = getAuthToken();
    if (token) {
        window.location.href = `/book/${bookId}`; // '/pdf/detail' -> '/book' 으로 변경
    } else {
        alert('로그인이 필요합니다.');
        window.location.href = '/auth/login';
    }
}
