// =================================================================================
// Global Functions (accessible by both pages)
// =================================================================================

// =================================================================================
// Global Functions (accessible by both pages)
// =================================================================================

/**
 * PDF 뷰어의 높이를 화면에 맞게 조정합니다.
 */
function adjustPdfViewerHeight() {
    const pdfViewer = document.getElementById('pdfViewer');
    if (!pdfViewer) return;
    const vh = window.innerHeight;
    const header = document.querySelector('header');
    const headerH = header ? header.offsetHeight : 0;
    pdfViewer.style.minHeight = `${vh - headerH}px`;
    pdfViewer.style.transform = 'scale(1.03)';
    const embed = pdfViewer.querySelector('embed');
    if (embed) {
        embed.style.height = `${vh - headerH}px`;
    }
}

/**
 * PDF Base64 데이터를 파싱하여 Raw PDF로 표시합니다.
 * @param {string} base64Data - Base64 인코딩된 PDF 데이터.
 */
function displayPdfAsRaw(base64Data) { // targetElement 인자 제거, pdfViewer 직접 참조
    const pdfViewer = document.getElementById('pdfViewer');
    if (!pdfViewer) {
        console.error('PDF를 렌더링할 타겟 엘리먼트(#pdfViewer)를 찾을 수 없습니다.');
        return;
    }
    try {
        const binaryString = atob(base64Data);
        const len = binaryString.length;
        const bytes = new Uint8Array(len);
        for (let i = 0; i < len; i++) {
            bytes[i] = binaryString.charCodeAt(i);
        }

        const blob = new Blob([bytes], {type: 'application/pdf'});
        const url = URL.createObjectURL(blob);

        const embed = document.createElement('embed');
        embed.src = url;
        embed.type = 'application/pdf';
        embed.width = '100%';
        embed.height = '100%';

        pdfViewer.innerHTML = '';
        pdfViewer.appendChild(embed);

        // embed 태그가 DOM에 추가된 직후에 높이 조정 로직 호출
        adjustPdfViewerHeight();
    } catch (error) {
        console.error('PDF display failed:', error);
        pdfViewer.innerHTML = '<p>PDF 표시에 실패했습니다.</p>';
    }
}

/**
 * Navigates to the book detail page.
 * @param {number} bookId - The ID of the book.
 */
function goToPdfDetail(bookId) {
    console.log(`[DEBUG] goToPdfDetail called with bookId: ${bookId}`);
    const token = getAuthToken();
    console.log(`[DEBUG] Auth token present: ${!!token}`);
    if (token) {
        console.log(`[DEBUG] Navigating to: /book/${bookId}`);
        window.location.href = `/book/${bookId}`; // book.html로 이동
    } else {
        console.log('[DEBUG] Token not found, redirecting to login.');
        alert('로그인이 필요합니다.');
        window.location.href = '/auth/login';
    }
}

// =================================================================================
// Scripts for book.html (PDF Viewer)
// =================================================================================

/**
 * Initializes the book viewer page.
 */
async function initBookPage() {
    const pdfViewer = document.getElementById('pdfViewer');
    if (!pdfViewer) return;

    // adjustPdfViewerHeight는 이제 전역 함수이므로 여기서 다시 정의할 필요 없음
    // initBookPage 시작 부분의 adjustSectionHeight() 호출 제거
    window.addEventListener('resize', adjustPdfViewerHeight); // 전역 함수로 변경

    // currentBookId는 book.html의 스크립트 블록에서 넘어옴
    if (typeof currentBookId !== 'undefined' && currentBookId !== null) {
        try {
            // apiCall 함수를 사용하여 PDF 상세 정보를 가져옴
            const bookDetail = await apiCall(`/api/book/detail/${currentBookId}`, 'GET');
            if (bookDetail && bookDetail.fileBase64) {
                displayPdfAsRaw(bookDetail.fileBase64); // 전역 displayPdfAsRaw 호출
            } else {
                pdfViewer.innerHTML = '<p>PDF 데이터를 찾을 수 없습니다.</p>';
            }
        } catch (error) {
            console.error('PDF 데이터를 가져오는 중 오류 발생:', error);
            pdfViewer.innerHTML = '<p>PDF 로딩 중 오류가 발생했습니다.</p>';
        }
    }
}

// =================================================================================
// Scripts for home.html (Book List & Upload)
// =================================================================================

/**
 * Initializes the home page.
 */
async function initHomePage() {
    if (typeof pdfjsLib !== 'undefined') {
        pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
    }

    const pdfInput = document.getElementById('pdfInput');

    if (getAuthToken()) {
        await loadPdfList();
    } else {
        if (pdfInput) {
            pdfInput.removeAttribute('accept');
            pdfInput.type = 'text';
            pdfInput.addEventListener('click', (e) => {
                e.preventDefault();
                alert("로그인 또는 회원가입을 해주세요.");
            }, { once: true });
        }
    }

    if (pdfInput) {
        pdfInput.addEventListener('change', handleFileUpload);
    }
}

/**
 * Fetches and displays the list of PDF books.
 */
async function loadPdfList() {
    try {
        const pdfList = await apiCall('/api/book/list', 'GET');
        if (Array.isArray(pdfList)) {
            displayPdfList(pdfList);
        }
    } catch (error) {
        console.error('PDF 목록 로드 실패:', error);
    }
}

/**
 * Renders the list of PDF books on the page.
 * @param {Array} pdfList - An array of book data objects.
 */
function displayPdfList(pdfList) {
    const pdfContents = document.querySelector('.pdf_contents');
    if (!pdfContents) return;

    const originalPlusArea = pdfContents.querySelector('li:last-child');

    pdfList.forEach(pdf => {
        const pdfItem = document.createElement('li');
        pdfItem.className = 'pdf_li';
        pdfItem.innerHTML = `
            <div class="file_area" style="cursor: pointer;" onclick="goToPdfDetail(${pdf.bookId});">
                <img src="http://localhost:8000/api/v1/pdf-first-page/${pdf.bookId}"
                     alt="${pdf.title}"
                     style="max-width: 100%; height: 100%; display: block; margin: auto; object-fit: contain;"
                     onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22200%22 height=%22200%22%3E%3Crect width=%22200%22 height=%22200%22 fill=%22%23f0f0f0%22/%3E%3Ctext x=%2250%25%22 y=%2250%25%22 dominant-baseline=%22middle%22 text-anchor=%22middle%22 fill=%22%23999%22%3EPDF%3C/text%3E%3C/svg%3E';">
            </div>
            <div class="pdf_title" onclick="goToPdfDetail(${pdf.bookId});">
                ${pdf.title}
            </div>`;
        if (originalPlusArea) {
            originalPlusArea.parentNode.insertBefore(pdfItem, originalPlusArea);
        }
    });
}

/**
 * Handles the file input change event.
 * @param {Event} event
 */
function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    if (file.type !== "application/pdf") {
        alert('PDF 파일만 업로드할 수 있습니다.');
        event.target.value = '';
        return;
    }

    if (typeof pdfjsLib === 'undefined') {
        alert("PDF.js 라이브러리가 로드되지 않아 처리를 시작할 수 없습니다.");
        return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
        const originalLi = event.target.closest('.pdf_contents > li');
        const { newElement, canvas } = createAndInsertPreviewElement(originalLi);
        processAndUploadPdf(e.target.result, file.name, newElement, canvas);
    };
    reader.readAsDataURL(file);
    event.target.value = '';
}

/**
 * Creates and inserts a new preview element into the DOM.
 * @param {HTMLElement} originalLi - The original 'li' element for uploading.
 * @returns {{newElement: HTMLElement, canvas: HTMLCanvasElement}}
 */
function createAndInsertPreviewElement(originalLi) {
    const newElement = originalLi.cloneNode(true);
    newElement.innerHTML = '';
    newElement.classList.add("pdf_li");

    const fileArea = document.createElement('div');
    fileArea.className = 'file_area';
    fileArea.style.zIndex = "1";
    
    const canvas = document.createElement('canvas');
    canvas.style.maxWidth = '100%';
    canvas.style.height = '100%';
    canvas.style.display = 'block';
    canvas.style.margin = 'auto';
    
    fileArea.appendChild(canvas);
    newElement.appendChild(fileArea);

    originalLi.parentNode.insertBefore(newElement, originalLi);
    return { newElement, canvas };
}


/**
 * Processes the PDF data for rendering and uploading.
 * @param {ArrayBuffer} pdfData
 * @param {string} fileName
 * @param {HTMLElement} newElement
 * @param {HTMLCanvasElement} canvas
 */
async function processAndUploadPdf(pdfBase64DataUrl, fileName, newElement, canvas) {
    try {
        // Render preview using the base64 data URL
        const pdf = await pdfjsLib.getDocument({ url: pdfBase64DataUrl }).promise;
        const page = await pdf.getPage(1);
        const viewport = page.getViewport({ scale: 1.1 });
        const context = canvas.getContext('2d');
        canvas.height = viewport.height;
        canvas.width = viewport.width;
        await page.render({ canvasContext: context, viewport: viewport }).promise;

        // Upload
        const pdfBase64 = pdfBase64DataUrl.split(',')[1];
        await uploadPdfToServer(fileName, pdfBase64); // This reloads on success

    } catch (error) {
        console.error('PDF 처리 또는 업로드 실패:', error);
        const errorMessage = error.message || '알 수 없는 오류가 발생했습니다.';
        alert(`PDF 처리 또는 업로드에 실패했습니다: ${errorMessage}`);
        if (newElement.parentNode) {
            newElement.parentNode.removeChild(newElement);
        }
    }
}


/**
 * Uploads the processed PDF data to the server.
 * @param {string} title
 * @param {string} fileBase64
 */
async function uploadPdfToServer(title, fileBase64) {
    const payload = {
        title: title,
        file_base64: fileBase64
    };
    const response = await apiCall('/api/book/upload', 'POST', payload);

    if (response && response.bookId) {
        window.location.reload();
    } else {
        throw new Error('bookId를 응답에서 찾을 수 없습니다.');
    }
}


// =================================================================================
// Main Entry Point
// =================================================================================

document.addEventListener('DOMContentLoaded', function () {
    if (document.getElementById('pdfViewer')) {
        initBookPage();
    }

    if (document.querySelector('.pdf_contents')) {
        initHomePage();
    }
});