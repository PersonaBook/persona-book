"""
문제 생성 관련 API
"""
from app.schemas.request.chat import UserMessageRequest
from app.schemas.response.chat import AiMessageResponse, GeneratingQuestionResponse
from app.schemas.enum import ChatState
from app.services.question_generator_service import question_generator_service
from app.services.pdf_service import pdf_service
from fastapi import APIRouter, HTTPException
import os

router = APIRouter()

# 전역 변수로 현재 문제의 정답 정보 저장
current_question_answer = {}


@router.post("/generating-question", response_model=GeneratingQuestionResponse)
def handle_generating_question(user: UserMessageRequest):
    """RAG와 로컬 임베딩을 모두 사용한 문제 생성 처리"""
    global current_question_answer
    try:
        print(f"🚀 문제 생성 API 호출됨")
        print(f"📊 요청 데이터: userId={user.userId}, bookId={user.bookId}, content='{user.content}'")
        
        # 사용자 입력을 챕터 내용으로 매핑 - 향상된 시스템 사용
        from app.utils.chapter_mapper import (
            map_chapter_to_content, 
            enhance_query_for_search, 
            extract_chapter_info,
            get_enhanced_chapter_content
        )
        
        raw_input = user.content if user.content else "Java 프로그래밍"
        
        # 챕터 번호 추출 시도
        chapter_num, _ = extract_chapter_info(raw_input)
        
        if chapter_num:
            # 정밀한 키워드 기반 매핑 사용
            mapped_content = get_enhanced_chapter_content(chapter_num)
            print(f"🔥 정밀 키워드 시스템 사용 - 챕터 {chapter_num}")
        else:
            # 기존 매핑 시스템 사용
            mapped_content = map_chapter_to_content(raw_input)
            print(f"🔄 기본 매핑 시스템 사용")
        
        query = enhance_query_for_search(mapped_content)
        
        print(f"📝 원본 입력: {raw_input}")
        print(f"📝 매핑된 내용: {mapped_content}")
        print(f"📝 최종 쿼리: {query}")
        
        # PDF 처리 및 청킹 (pdf_service 사용)
        pdf_path = "/app/javajungsuk4_sample.pdf"
        if os.path.exists(pdf_path):
            print(f"📄 PDF 파일 처리 중: {pdf_path}")
            chunks = pdf_service().process_pdf_and_create_chunks(pdf_path, max_pages=20)
            print(f"✅ PDF 처리 완료: {len(chunks) if chunks else 0}개 청크")
        else:
            print(f"❌ PDF 파일을 찾을 수 없음: {pdf_path}")
            chunks = None
        
        if chunks:
            # 벡터 스토어 설정
            print(f"🔧 벡터 스토어 설정 중...")
            success = question_generator_service.setup_vector_store(chunks)
            print(f"✅ 벡터 스토어 설정: {'성공' if success else '실패'}")
            
            if success:
                # 문제 생성
                print(f"🎯 문제 생성 중...")
                result = question_generator_service.generate_question_with_rag(
                    query=query,
                    difficulty="보통",
                    question_type="객관식"
                )
                print(f"✅ 문제 생성 완료: {result.get('success', False)}")
                
                if result.get("success", False):
                    # 문제와 정답 정보를 함께 저장
                    question = result.get("question", "문제가 생성되었습니다.")
                    answer = result.get("correct_answer", "")
                    explanation = result.get("explanation", "")
                    options = result.get("options", [])
                    
                    # 문제 텍스트 생성 (정답 정보는 제외)
                    if options and len(options) > 0:
                        # 객관식인 경우 선택지 포함
                        content = f"{question}\n\n"
                        for i, option in enumerate(options, 1):
                            content += f"{i}. {option}\n"
                        print(f"✅ 선택지 포함된 문제 생성 완료")
                    else:
                        # 주관식인 경우 문제만
                        content = f"{question}"
                        print(f"⚠️ 선택지가 없어 주관식으로 생성됨")
                    
                    # 정답 정보를 세션에 저장
                    current_question_answer = {
                        "answer": answer,
                        "explanation": explanation
                    }
                else:
                    content = result.get("message", "문제 생성에 실패했습니다.")
                    print(f"❌ 문제 생성 실패: {content}")
            else:
                content = "문서 설정에 실패했습니다."
                print(f"❌ 벡터 스토어 설정 실패")
        else:
            content = "PDF 처리에 실패했습니다."
            print(f"❌ PDF 처리 실패")
        
        # 최종 응답에서 정답 정보 제거
        import re
        final_content = re.sub(r'\[정답 정보:.*?\]', '', content, flags=re.DOTALL).strip()
        final_content = re.sub(r'정답 정보:.*?$', '', final_content, flags=re.DOTALL).strip()
        final_content = re.sub(r'\[정답.*?\]', '', final_content, flags=re.DOTALL).strip()
        final_content = re.sub(r'정답.*?$', '', final_content, flags=re.DOTALL).strip()
        print(f"🔍 최종 응답 content: {final_content}")
        
        # domain과 concept 추출 (사용자 입력에서)
        domain = "Java Programming"  # 기본값
        concept = mapped_content if mapped_content else raw_input
        
        return GeneratingQuestionResponse(
            userId=user.userId,
            bookId=user.bookId,
            content=final_content,
            messageType="TEXT",
            sender="AI",
            chatState=ChatState.GENERATING_QUESTION_WITH_RAG,
            domain=domain,
            concept=concept,
            problem_text=question if 'question' in locals() else final_content,
            correct_answer=current_question_answer.get("answer", "")
        )
    except Exception as e:
        print(f"❌ 문제 생성 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"문제 생성 중 오류가 발생했습니다: {str(e)}")


@router.post("/generating-additional-question", response_model=GeneratingQuestionResponse)
def handle_generating_additional_question(user: UserMessageRequest):
    """추가 문제 생성 처리"""
    try:
        print(f"🚀 추가 문제 생성 API 호출됨")
        
        # 기존 문제와 유사한 추가 문제 생성
        query = user.content if user.content else "Java 프로그래밍"
        
        # 추가 문제 생성 (기존과 다른 유형)
        result = question_generator_service.generate_question_with_rag(
            query=query,
            difficulty="보통",
            question_type="주관식"  # 다른 유형으로 생성
        )
        
        # 결과가 딕셔너리인 경우 처리
        if isinstance(result, dict):
            if result.get("success", False):
                content = result.get("question", "추가 문제가 생성되었습니다.")
            else:
                content = result.get("message", "추가 문제 생성에 실패했습니다.")
        else:
            # 문자열인 경우 그대로 사용
            content = str(result)
        
        # 추가 문제에서도 필수 필드들 포함
        domain = "Java Programming"
        concept = query
        
        # 추가 문제의 정답 정보도 저장
        global current_question_answer
        if isinstance(result, dict) and result.get("success", False):
            current_question_answer = {
                "answer": result.get("correct_answer", ""),
                "explanation": result.get("explanation", "")
            }
            problem_text = result.get("question", content)
            correct_answer = result.get("correct_answer", "")
        else:
            problem_text = content
            correct_answer = ""
        
        return GeneratingQuestionResponse(
            userId=user.userId,
            bookId=user.bookId,
            content=content,
            messageType="TEXT",
            sender="AI",
            chatState=ChatState.GENERATING_ADDITIONAL_QUESTION,
            domain=domain,
            concept=concept,
            problem_text=problem_text,
            correct_answer=correct_answer
        )
    except Exception as e:
        print(f"❌ 추가 문제 생성 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"추가 문제 생성 중 오류가 발생했습니다: {str(e)}")