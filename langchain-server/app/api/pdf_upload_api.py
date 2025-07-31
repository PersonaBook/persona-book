"""
PDF 업로드 및 임베딩 처리 API
"""
import base64
import os
import tempfile
from fastapi import APIRouter, HTTPException
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
        
        # 임시 파일로 저장
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_file.write(pdf_bytes)
            temp_pdf_path = temp_file.name
        
        try:
            # PDF 처리 및 임베딩 생성
            chunks_created = process_pdf_and_create_embeddings(
                temp_pdf_path, 
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
            
        finally:
            # 임시 파일 삭제
            if os.path.exists(temp_pdf_path):
                os.unlink(temp_pdf_path)
                
    except Exception as e:
        print(f"❌ PDF 업로드 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"PDF 업로드 중 오류가 발생했습니다: {str(e)}")

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