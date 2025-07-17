import os
import re  # re 모듈 추가
import shutil  # shutil 모듈 추가
import tempfile

import cv2  # OpenCV
import fitz  # PyMuPDF
import streamlit as st
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (PyPDFLoader,
                                                  UnstructuredImageLoader,
                                                  UnstructuredPDFLoader)


def preprocess_pdf_page(pdf_path, page_number, temp_dir):
    doc = fitz.open(pdf_path)
    page = doc[page_number]
    pix = page.get_pixmap()
    img_path = os.path.join(temp_dir, f"page-{page_number:03d}.png")
    pix.save(img_path)
    doc.close()

    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    _, th = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,1))
    clean = cv2.morphologyEx(th, cv2.MORPH_OPEN, kernel)
    h, w = clean.shape
    clean = cv2.resize(clean, (w*2, h*2), interpolation=cv2.INTER_LINEAR)
    preprocessed_img_path = os.path.join(temp_dir, f"preprocessed_page-{page_number:03d}.png")
    cv2.imwrite(preprocessed_img_path, clean)
    return preprocessed_img_path


def main():
    st.title("PDF 문서 처리 및 청킹")
    st.divider()

    loader_type = "UnstructuredPDFLoader (고품질)"
    ocr_strategy = "hi_res"
    ocr_languages = "kor+eng"

    pdf_file = st.file_uploader("PDF 파일을 업로드하세요", type="pdf")

    

    if pdf_file is not None:
        # 업로드된 파일을 임시 파일로 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(pdf_file.getvalue())
            tmp_file_path = tmp_file.name
        
        try:
            # 1) 페이지별 Document 로드 (이미지 전처리 후 로드)
            page_docs = []
            temp_img_dir = tempfile.mkdtemp() # 임시 이미지 저장 디렉토리 생성
            
            pdf_document = fitz.open(tmp_file_path)
            for page_num in range(pdf_document.page_count):
                preprocessed_img_path = preprocess_pdf_page(tmp_file_path, page_num, temp_img_dir)
                image_loader = UnstructuredImageLoader(
                    preprocessed_img_path,
                    strategy=ocr_strategy,
                    ocr_languages=ocr_languages
                )
                page_docs.extend(image_loader.load())
            pdf_document.close()

            # 특정 문자열 제거를 위한 정규 표현식
            # 실제 출력되는 텍스트에 맞게 패턴 수정 (SBA, ~, 이메일 포함)
            pattern_to_remove = r"\[ebook\s*-\s*샘플\.\s*무료\s*공유\]\s*자\s*바\s*의\s*정석\s*4\s*판\s*Java\s*21\s*SBA\s*2025\.\s*7\.\s*7\s*출시\s*~?seong\.namkung@gmail\.com"
            
            for doc in page_docs:
                # 불필요한 텍스트 제거
                doc.page_content = re.sub(pattern_to_remove, "", doc.page_content)
                
                

            st.subheader("원본 문서 정보:")
            if page_docs:
                # 추출된 텍스트를 파일로 저장 (디버깅용)
                output_file_path = os.path.join(tempfile.gettempdir(), "extracted_text.txt")
                with open(output_file_path, "w", encoding="utf-8") as f:
                    for i, doc in enumerate(page_docs):
                        st.write(f"문서 {i+1}: 페이지 {doc.metadata.get('page_number', 'N/A')}, 소스: {doc.metadata.get('source', 'N/A')}")
                        st.write(f"메타데이터: {doc.metadata}")
                        st.subheader(f"페이지 {i+1} 전체 내용:")
                        st.text_area(f"페이지 {i+1} 텍스트", doc.page_content, height=400)
                        f.write(f"--- Page {doc.metadata.get('page_number', 'N/A')} ---\n")
                        f.write(doc.page_content)
                        f.write("\n\n")
                st.success(f"추출된 텍스트가 다음 위치에 저장되었습니다: {output_file_path}")
            else:
                st.warning("PDF에서 문서를 로드할 수 없습니다. 파일이 비어있거나 손상되었을 수 있습니다.")

            # 2) 의미 단위 청킹(메타데이터 보존) - 주석 처리됨
            # splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
            # chunks = splitter.split_documents(page_docs)

            # st.subheader("청크 정보:")
            # if chunks:
            #     for i, chunk in enumerate(chunks):
            #         page_info = chunk.metadata.get('page_number', 'N/A')
            #         st.write(f"청크 {i+1}: 페이지 {page_info}")
            #         st.subheader(f"청크 {i+1} 전체 내용:")
            #         st.text_area(f"청크 {i+1} 텍스트", chunk.page_content, height=200)
            # else:
            #     st.warning("추출된 청크가 없습니다.")

        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
            st.exception(e)
        finally:
            # 임시 파일 삭제
            os.remove(tmp_file_path)
            if 'temp_img_dir' in locals() and os.path.exists(temp_img_dir):
                shutil.rmtree(temp_img_dir)

if __name__ == '__main__':
    main()