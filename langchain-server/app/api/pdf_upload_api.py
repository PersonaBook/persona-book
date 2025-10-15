"""
PDF 업로드 및 임베딩 처리 API
"""
import base64
import os
import tempfile
import fitz  # PyMuPDF
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.services.pdf_service import get_pdf_service
from app.services.question_generator_service import question_generator_service
from app.schemas.response.chat import AiMessageResponse
from app.schemas.enum import ChatState

router = APIRouter()

class PdfUploadRequest(BaseModel):
    pdf_base64: str
    bookId: int
    userId: int
    query: Optional[str] = "Java 프로그래밍"
    max_pages: Optional[int] = 20

class PdfUploadResponse(BaseModel):
    success: bool
    message: str
    bookId: int
    userId: int
    chunks_created: Optional[int] = 0

@router.post("/pdf-upload", response_model=PdfUploadResponse)
def handle_pdf_upload(request: PdfUploadRequest):
    """
    PDF를 업로드하고 임베딩을 생성합니다.
    """
    try:
        print(f"🚀 PDF 업로드 시작 - BookId: {request.bookId}, UserId: {request.userId}")

        # Base64를 PDF 파일로 변환
        pdf_bytes = base64.b64decode(request.pdf_base64)

        # PDF 저장 디렉토리 생성
        pdf_storage_dir = "/app/pdf_storage"
        os.makedirs(pdf_storage_dir, exist_ok=True)

        # bookId로 PDF 파일 저장 (영구 저장)
        pdf_file_path = os.path.join(pdf_storage_dir, f"book_{request.bookId}.pdf")

        with open(pdf_file_path, "wb") as f:
            f.write(pdf_bytes)

        print(f"✅ PDF 파일 저장 완료: {pdf_file_path}")

        # PDF 처리 및 임베딩 생성
        chunks_created = process_pdf_and_create_embeddings(
            pdf_file_path,
            request.bookId,
            request.userId,
            request.max_pages
        )

        return PdfUploadResponse(
            success=True,
            message="PDF 업로드 및 임베딩 생성이 완료되었습니다.",
            bookId=request.bookId,
            userId=request.userId,
            chunks_created=chunks_created
        )

    except Exception as e:
        print(f"❌ PDF 업로드 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"PDF 업로드 중 오류가 발생했습니다: {str(e)}")

@router.get("/pdf-first-page/{book_id}")
async def get_pdf_first_page(book_id: int):
    """
    PDF의 첫 페이지를 PNG 이미지로 반환합니다.
    """
    try:
        print(f"🖼️ PDF 첫 페이지 요청 - BookId: {book_id}")

        # bookId에 해당하는 PDF 파일 경로
        pdf_storage_dir = "/app/pdf_storage"
        pdf_path = os.path.join(pdf_storage_dir, f"book_{book_id}.pdf")

        # 해당 bookId의 PDF가 없으면 기본 PDF 사용
        if not os.path.exists(pdf_path):
            print(f"⚠️ BookId {book_id}의 PDF가 없어 기본 PDF 사용")
            pdf_path = "/app/javajungsuk4_sample.pdf"

        if not os.path.exists(pdf_path):
            raise HTTPException(status_code=404, detail="PDF 파일을 찾을 수 없습니다.")

        # PDF 첫 페이지를 이미지로 변환
        doc = fitz.open(pdf_path)

        if len(doc) == 0:
            doc.close()
            raise HTTPException(status_code=400, detail="PDF에 페이지가 없습니다.")

        # 첫 페이지 가져오기
        first_page = doc[0]

        # 페이지를 이미지로 렌더링 (해상도 300 DPI)
        mat = fitz.Matrix(2.0, 2.0)  # 2배 확대 (더 선명한 이미지)
        pix = first_page.get_pixmap(matrix=mat)

        # PNG 바이트로 변환
        img_bytes = pix.tobytes("png")

        doc.close()

        print(f"✅ PDF 첫 페이지 이미지 생성 완료: {len(img_bytes)} bytes")

        return Response(content=img_bytes, media_type="image/png")

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ PDF 첫 페이지 생성 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"PDF 첫 페이지 생성 중 오류가 발생했습니다: {str(e)}")


def process_pdf_and_create_embeddings(pdf_path: str, book_id: int, user_id: int, max_pages: int = 20) -> int:
    """
    PDF를 처리하고 벡터 스토어에 임베딩을 생성합니다.
    """
    try:
        # PDF에서 텍스트 추출 및 청킹
        pdf_service = get_pdf_service()
        chunks = pdf_service.process_pdf_and_create_chunks(pdf_path, max_pages=max_pages)

        if not chunks:
            raise Exception("PDF에서 텍스트를 추출할 수 없습니다.")

        print(f"✅ PDF 청킹 완료: {len(chunks)}개 청크 생성")

        # 벡터 스토어 설정
        index_name = f"java_learning_docs_book_{book_id}"
        success = question_generator_service.setup_vector_store(chunks, index_name)

        if not success:
            raise Exception("벡터 스토어 설정에 실패했습니다.")

        print(f"✅ 벡터 스토어 설정 완료: {index_name}")

        return len(chunks)

    except Exception as e:
        print(f"❌ PDF 처리 오류: {str(e)}")
        raise e