$(document).ready(function () {
    console.log('main/script.js 실행');

    if (getAuthToken()) {
        loadPdfList();
    }

    $('#imageInput').on('change', function (event) {
        const file = this.files[0];
        const $originalPlusArea = $(this).closest('.pdf_contents > li');

        if (file) {
            if (file.type === "application/pdf") {
                if (typeof pdfjsLib === 'undefined') {
                    alert("PDF.js 라이브러리가 로드되지 않아 PDF를 미리 볼 수 없습니다.");
                    // 원본 미리보기 영역에 메시지 표시
                    $originalPlusArea.find('#imagePreview').html('<p style="color: red;">PDF.js 라이브러리 로드 오류.</p>');
                    $(this).val('');
                    return;
                }

                const reader = new FileReader();

                reader.onload = function (e) {
                    const pdfData = e.target.result;


                    // 전체 PDF 파일을 base64로 변환 (청크 단위로 처리)
                    const uint8Array = new Uint8Array(pdfData);
                    let binaryString = '';
                    const chunkSize = 8192; // 8KB씩 처리
                    for (let i = 0; i < uint8Array.length; i += chunkSize) {
                        const chunk = uint8Array.slice(i, i + chunkSize);
                        binaryString += String.fromCharCode.apply(null, chunk);
                    }
                    const pdfBase64 = btoa(binaryString);


                    // PDF.js를 사용하여 PDF 로드
                    const loadingTask = pdfjsLib.getDocument({data: pdfData});
                    loadingTask.promise.then(function (pdf) {
                        // 첫 번째 페이지 가져오기
                        pdf.getPage(1).then(function (page) {
                            // 1. 새로운 .plus_area 구조 복제
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

                            const $canvas = $('<canvas><a href=""></a></canvas>');
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

                            // PDF 페이지 렌더링
                            const renderContext = {
                                canvasContext: context,
                                viewport: viewport
                            };
                            page.render(renderContext).promise.then(function () {
                                console.log('PDF rendered on new canvas!');


                                // 전체 PDF 파일을 서버에 업로드 (이미 변환된 base64 사용)
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
                // 지원하지 않는 파일 형식
                $originalPlusArea.find('#imagePreview').html('<p style="color: red;">지원하지 않는 파일 형식입니다. </br>(PDF 또는 이미지)</p>');
                $(this).val('');
            }
        } else {
            $originalPlusArea.find('#imagePreview').html('<p></p>');
        }
    });
});

function loadPdfList() {
    $.ajax({
        url: '/api/pdf/list',
        type: 'GET',
        headers: {
            'Authorization': 'Bearer ' + getAuthToken()
        },
        success: function (response) {
            if (Array.isArray(response)) {
                displayPdfList(response);
            }
        },
        error: function (xhr) {
            if (xhr.status === 401) {
                alert('로그인이 필요합니다.');
                window.location.href = '/user/login';
            } else {
                console.error('PDF 목록 로드 실패:', xhr.responseText);
            }
        }
    });
}

function displayPdfList(pdfList) {
    const $pdfContents = $('.pdf_contents');
    const $originalPlusArea = $pdfContents.find('li:last-child');

    pdfList.forEach(function (pdf) {
        const $pdfItem = $('<div class="pdf-item"></div>');
        $pdfItem.html(`
            <li class="pdf_li">
                <div class="file_area" style="cursor: pointer;" onclick="goToPdfDetail(${pdf.bookId})">
                    <canvas style="max-width: 100%; height: 100%; display: block; margin: auto;"></canvas>
                </div>
            </li>
            <p class="pdf_title">${pdf.title}</p>
        `);

        if (pdf.fileBase64) {
            renderPdfPreview(pdf.fileBase64, $pdfItem.find('canvas')[0]);
        }

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
    $.ajax({
        url: '/api/pdf/upload',
        type: 'POST',
        contentType: 'application/json',
        headers: {
            'Authorization': 'Bearer ' + getAuthToken()
        },
        data: JSON.stringify({
            title: title,
            file_base64: fileBase64
        }),
        success: function (response) {
            if (response.success) {
                console.log('PDF 업로드 성공:', response);
                $pdfElement.attr('onclick', `goToPdfDetail(${response.bookId})`);
                $pdfElement.find('.file_area').attr('onclick', `goToPdfDetail(${response.bookId})`);
                $pdfElement.append(`<p class="pdf_title">${title}</p>`);
            } else {
                alert('PDF 업로드 실패: ' + response.message);
                $pdfElement.remove();
            }
        },
        error: function (xhr) {
            console.error('PDF 업로드 실패:', xhr.responseText);
            alert('PDF 업로드 실패');
            $pdfElement.remove();
        }
    });
}

function goToPdfDetail(bookId) {
    const token = getAuthToken();
    if (token) {
        window.location.href = `/pdf/detail/${bookId}`;
    } else {
        alert('로그인이 필요합니다.');
        window.location.href = '/user/login';
    }
}
