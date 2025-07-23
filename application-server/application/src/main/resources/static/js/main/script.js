$(document).ready(function() {
    $('#imageInput').on('change', function(event) {
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

                reader.onload = function(e) {
                    const pdfData = e.target.result;

                    // PDF.js를 사용하여 PDF 로드
                    const loadingTask = pdfjsLib.getDocument({ data: pdfData });
                    loadingTask.promise.then(function(pdf) {
                        // 첫 번째 페이지 가져오기
                        pdf.getPage(1).then(function(page) {
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
                            const viewport = page.getViewport({ scale: scale });

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
                            page.render(renderContext).promise.then(function() {
                                console.log('PDF rendered on new canvas!');
                            });

                            $originalPlusArea.before($newPlusArea);

                            $originalPlusArea.find('#imagePreview').html('<p></p>');
                            $(event.target).val('');

                        }).catch(function(error) {
                            console.error('Error getting PDF page:', error);
                            $originalPlusArea.find('#imagePreview').html('<p style="color: red;">PDF 페이지 로드 실패.</p>');
                        });
                    }).catch(function(error) {
                        console.error('Error loading PDF document:', error);
                        $originalPlusArea.find('#imagePreview').html('<p style="color: red;">PDF 문서 로드 실패.</p>');
                    });
                };

                reader.readAsArrayBuffer(file);
            } else if (file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = function(e) {
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