
"""
문제 생성 관련 API
"""
from app.schemas.request.chat import UserMessageRequest
from app.schemas.response.chat import AiMessageResponse, GeneratingQuestionResponse
from app.schemas.enum import ChatState
from app.services.question_generator_service import question_generator_service
from app.services.pdf_service import pdf_service
from fastapi import APIRouter, HTTPException, File, UploadFile, Form, Request
import os

router = APIRouter()

# 전역 변수로 현재 문제의 정답 정보 저장
current_question_answer = {}


# PDF 업로드를 지원하는 새로운 엔드포인트
@router.post("/generating-question-with-file", response_model=GeneratingQuestionResponse)
async def handle_generating_question_with_file(
    pdf_file: UploadFile = File(None),
    userId: int = Form(...),
    bookId: int = Form(...),
    content: str = Form(""),
    chatState: str = Form("GENERATING_QUESTION_WITH_RAG")
):
    """PDF 파일 업로드를 지원하는 문제 생성 처리"""
    global current_question_answer
    # 새로운 문제 생성 시 이전 정답 정보 초기화
    current_question_answer = {}

    try:
        print("=" * 80)
        print(f"🚀🚀🚀 PDF 파일 업로드 문제 생성 API 호출됨!!! 🚀🚀🚀")
        print(f"📊 요청 데이터: userId={userId}, bookId={bookId}")
        print(f"📊 사용자 입력: '{content}'")
        print(f"📊 ChatState: {chatState}")
        print(f"📊 PDF 파일: {pdf_file.filename if pdf_file else 'None'}")
        print("=" * 80)

        # PDF 파일이 업로드된 경우 처리
        if pdf_file and pdf_file.filename:
            # 임시 파일로 저장
            temp_pdf_path = f"/tmp/{pdf_file.filename}"
            with open(temp_pdf_path, "wb") as f:
                pdf_content = await pdf_file.read()
                f.write(pdf_content)
            print(f"📄 업로드된 PDF 저장: {temp_pdf_path}")
        else:
            # 기본 PDF 사용
            temp_pdf_path = "/app/javajungsuk4_sample.pdf"

        # 기존 처리 로직 사용
        raw_input = content if content else "Java 프로그래밍"

        # 챕터 정보 처리
        from app.utils.chapter_mapper import (
            map_chapter_to_content,
            enhance_query_for_search,
            extract_chapter_info,
            get_enhanced_chapter_content
        )

        chapter_num, _ = extract_chapter_info(raw_input)

        if chapter_num:
            mapped_content = get_enhanced_chapter_content(chapter_num)
            print(f"🔥 정밀 키워드 시스템 사용 - 챕터 {chapter_num}")
        else:
            mapped_content = map_chapter_to_content(raw_input)
            print(f"🔄 기본 매핑 시스템 사용")

        query = enhance_query_for_search(mapped_content)

        print(f"📝 원본 입력: {raw_input}")
        print(f"📝 매핑된 내용: {mapped_content}")
        print(f"📝 최종 쿼리: {query}")

        # PDF 처리 및 문제 생성
        if os.path.exists(temp_pdf_path):
            print(f"📄 PDF 파일 처리 중: {temp_pdf_path}")

            max_pages_to_process = 50
            if chapter_num:
                from app.utils.chapter_mapper import get_chapter_definitions
                chapter_defs = get_chapter_definitions()
                if chapter_num in chapter_defs:
                    chapter_start_page = chapter_defs[chapter_num].get("start", 50)
                    chapter_end_page = chapter_defs[chapter_num]["end"]
                    max_pages_to_process = min(chapter_end_page - chapter_start_page + 20, 50)
                    print(f"🎯 챕터 {chapter_num} 기준 PDF 처리: {max_pages_to_process}페이지까지")

            chunks = pdf_service().process_pdf_and_create_chunks(temp_pdf_path, max_pages=max_pages_to_process)
            print(f"✅ PDF 처리 완료: {len(chunks) if chunks else 0}개 청크")

            if chunks:
                print(f"🔧 벡터 스토어 설정 중...")
                success = question_generator_service.setup_vector_store(chunks)
                print(f"✅ 벡터 스토어 설정: {'성공' if success else '실패'}")
            else:
                success = False

            # 임시 파일 삭제 (업로드된 파일인 경우)
            if pdf_file and pdf_file.filename and temp_pdf_path != "/app/javajungsuk4_sample.pdf":
                try:
                    os.remove(temp_pdf_path)
                    print(f"🗑️ 임시 파일 삭제: {temp_pdf_path}")
                except:
                    pass
        else:
            print(f"❌ PDF 파일을 찾을 수 없음: {temp_pdf_path}")
            success = False

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
                question = result.get("question", "문제가 생성되었습니다.")
                answer = result.get("correct_answer", "")
                explanation = result.get("explanation", "")
                options = result.get("options", [])

                if options and len(options) > 0:
                    content_text = f"{question}\n\n"
                    for i, option in enumerate(options, 1):
                        content_text += f"{i}. {option}\n"
                    print(f"✅ 선택지 포함된 문제 생성 완료")
                else:
                    content_text = f"{question}"
                    print(f"⚠️ 선택지가 없어 주관식으로 생성됨")

                current_question_answer = {
                    "answer": answer,
                    "explanation": explanation
                }
            else:
                content_text = result.get("message", "문제 생성에 실패했습니다.")
                print(f"❌ 문제 생성 실패: {content_text}")
        else:
            content_text = "문서 설정에 실패했습니다."
            print(f"❌ 벡터 스토어 설정 실패")

        # ChatState enum으로 변환
        from app.schemas.enum import ChatState as ChatStateEnum
        try:
            chat_state_enum = ChatStateEnum(chatState)
        except ValueError:
            chat_state_enum = ChatStateEnum.GENERATING_QUESTION_WITH_RAG

        # 최종 응답
        import re
        final_content = re.sub(r'\[정답 정보:.*?\]', '', content_text, flags=re.DOTALL).strip()
        final_content = re.sub(r'정답 정보:.*?$', '', final_content, flags=re.DOTALL).strip()
        final_content = re.sub(r'\[정답.*?\]', '', final_content, flags=re.DOTALL).strip()
        final_content = re.sub(r'정답.*?$', '', final_content, flags=re.DOTALL).strip()
        final_content = final_content.replace('```', '')

        print(f"🔍 최종 응답 content: {final_content}")

        domain = "Java Programming"
        concept = (mapped_content if mapped_content else raw_input)[:200]

        return GeneratingQuestionResponse(
            userId=userId,
            bookId=bookId,
            content=final_content,
            messageType="TEXT",
            sender="AI",
            chatState=chat_state_enum,
            domain=domain,
            concept=concept,
            problemText=question if 'question' in locals() else final_content,
            correctAnswer=answer if 'answer' in locals() else current_question_answer.get("answer", "")
        )
    except Exception as e:
        print(f"❌ PDF 업로드 문제 생성 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"PDF 업로드 문제 생성 중 오류가 발생했습니다: {str(e)}")

@router.post("/generating-question", response_model=GeneratingQuestionResponse)
async def handle_generating_question(request: Request):
    """RAG와 로컬 임베딩을 모두 사용한 문제 생성 처리 - JSON과 multipart 지원"""
    global current_question_answer
    # 새로운 문제 생성 시 이전 정답 정보 초기화
    current_question_answer = {}

    try:
        # Content-Type 확인
        content_type = request.headers.get("content-type", "")

        if "multipart/form-data" in content_type:
            # PDF 업로드 요청
            print("🔄 PDF 업로드 요청 감지")
            form = await request.form()

            # 폼 데이터에서 정보 추출
            pdf_file = form.get("pdf_file")
            userId = int(form.get("userId", 1))
            bookId = int(form.get("bookId", 1))

            # application-server에서 보내는 필드명 지원 (content 또는 query)
            content = form.get("content", form.get("query", ""))
            chatState = form.get("chatState", "GENERATING_QUESTION_WITH_RAG")

            print(f"📋 폼 데이터: userId={userId}, bookId={bookId}, content='{content}', pdf_file={pdf_file.filename if pdf_file else 'None'}")

            # PDF 파일이 업로드된 경우 처리
            if pdf_file and pdf_file.filename:
                # 임시 파일로 저장
                temp_pdf_path = f"/tmp/{pdf_file.filename}"
                with open(temp_pdf_path, "wb") as f:
                    pdf_content = await pdf_file.read()
                    f.write(pdf_content)
                print(f"📄 업로드된 PDF 저장: {temp_pdf_path}")
            else:
                # 기본 PDF 사용
                temp_pdf_path = "/app/javajungsuk4_sample.pdf"

        elif "application/json" in content_type:
            # JSON 요청
            print("🔄 JSON 요청 감지")
            json_data = await request.json()

            # UserMessageRequest 구조에 맞춰 데이터 추출
            user = UserMessageRequest(**json_data)
            userId = user.userId
            bookId = user.bookId
            content = user.content
            chatState = user.chatState.value
            temp_pdf_path = "/app/javajungsuk4_sample.pdf"  # 기본 PDF 사용

            print(f"📋 JSON 데이터: userId={userId}, bookId={bookId}, content='{content}'")
        else:
            raise HTTPException(status_code=400, detail="지원하지 않는 Content-Type입니다.")

        print("=" * 80)
        print(f"🚀🚀🚀 문제 생성 API 호출됨!!! 🚀🚀🚀")
        print(f"📊 요청 타입: {content_type}")
        print(f"📊 요청 데이터: userId={userId}, bookId={bookId}")
        print(f"📊 사용자 입력: '{content}'")
        print(f"📊 ChatState: {chatState}")
        print("=" * 80)

    except Exception as e:
        print(f"❌ 요청 처리 중 오류: {str(e)}")
        raise HTTPException(status_code=400, detail=f"요청 처리 중 오류가 발생했습니다: {str(e)}")

    try:
        # 사용자 입력을 챕터 내용으로 매핑 - 향상된 시스템 사용
        from app.utils.chapter_mapper import (
            map_chapter_to_content,
            enhance_query_for_search,
            extract_chapter_info,
            get_enhanced_chapter_content
        )

        raw_input = content if content else "Java 프로그래밍"
        
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
        
        # 기존 벡터 스토어가 있는지 확인 (성능 최적화)
        print(f"🔍 기존 벡터 스토어 확인 중...")
        if not question_generator_service.has_vector_store():
            print(f"📄 PDF 처리 필요 - 첫 번째 실행")
            # PDF 처리 및 청킹 (한 번만)
            pdf_path = temp_pdf_path
            if os.path.exists(pdf_path):
                print(f"📄 PDF 파일 처리 중: {pdf_path}")
                
                # 성능 최적화: 페이지 수를 대폭 줄임
                max_pages_to_process = 50  # 기본값을 줄임 (빠른 처리를 위해)
                if chapter_num:
                    from app.utils.chapter_mapper import get_chapter_definitions
                    chapter_defs = get_chapter_definitions()
                    if chapter_num in chapter_defs:
                        chapter_start_page = chapter_defs[chapter_num].get("start", 50)
                        chapter_end_page = chapter_defs[chapter_num]["end"]
                        # 해당 챕터만 처리 (시작-끝 페이지)
                        max_pages_to_process = min(chapter_end_page - chapter_start_page + 20, 50)
                        print(f"🎯 챕터 {chapter_num} 기준 PDF 처리: {max_pages_to_process}페이지까지")
                
                chunks = pdf_service().process_pdf_and_create_chunks(pdf_path, max_pages=max_pages_to_process)
                print(f"📊 실제 처리한 페이지 수: {max_pages_to_process}")
                print(f"✅ PDF 처리 완료: {len(chunks) if chunks else 0}개 청크")
                
                if chunks:
                    # 벡터 스토어 설정 (한 번만)
                    print(f"🔧 벡터 스토어 설정 중...")
                    success = question_generator_service.setup_vector_store(chunks)
                    print(f"✅ 벡터 스토어 설정: {'성공' if success else '실패'}")
                else:
                    success = False
            else:
                print(f"❌ PDF 파일을 찾을 수 없음: {pdf_path}")
                success = False
        else:
            print(f"🚀 기존 벡터 스토어 사용 - PDF 처리 생략")
            success = question_generator_service.connect_to_existing_vector_store()
            
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
        
        # 최종 응답에서 정답 정보 제거
        import re
        final_content = re.sub(r'\[정답 정보:.*?\]', '', content, flags=re.DOTALL).strip()
        final_content = re.sub(r'정답 정보:.*?$', '', final_content, flags=re.DOTALL).strip()
        final_content = re.sub(r'\[정답.*?\]', '', final_content, flags=re.DOTALL).strip()
        final_content = re.sub(r'정답.*?$', '', final_content, flags=re.DOTALL).strip()

        # 마크다운 코드 블록 제거
        final_content = final_content.replace('```', '')

        print(f"🔍 최종 응답 content: {final_content}")

        # domain과 concept 추출 (사용자 입력에서)
        domain = "Java Programming"  # 기본값
        concept = (mapped_content if mapped_content else raw_input)[:200]  # 200자로 제한

        # ChatState enum으로 변환
        from app.schemas.enum import ChatState as ChatStateEnum
        try:
            if isinstance(chatState, str):
                chat_state_enum = ChatStateEnum(chatState)
            else:
                chat_state_enum = chatState
        except ValueError:
            chat_state_enum = ChatStateEnum.GENERATING_QUESTION_WITH_RAG

        # 임시 파일 정리 (업로드된 PDF인 경우)
        if "multipart/form-data" in content_type and temp_pdf_path != "/app/javajungsuk4_sample.pdf":
            try:
                os.remove(temp_pdf_path)
                print(f"🗑️ 임시 파일 삭제: {temp_pdf_path}")
            except:
                pass

        return GeneratingQuestionResponse(
            userId=userId,
            bookId=bookId,
            content=final_content,
            messageType="TEXT",
            sender="AI",
            chatState=chat_state_enum,
            domain=domain,
            concept=concept,
            problemText=question if 'question' in locals() else final_content,
            correctAnswer=answer if 'answer' in locals() else current_question_answer.get("answer", "")
        )
    except Exception as e:
        print(f"❌ 문제 생성 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"문제 생성 중 오류가 발생했습니다: {str(e)}")


@router.post("/generating-additional-question", response_model=GeneratingQuestionResponse)
async def handle_generating_additional_question(user: UserMessageRequest):
    """추가 문제 생성 처리"""
    global current_question_answer
    # 새로운 문제 생성 시 이전 정답 정보 초기화
    current_question_answer = {}
    
    try:
        print(f"🚀 추가 문제 생성 API 호출됨")
        
        # 기존 문제와 유사한 추가 문제 생성
        query = user.content if user.content else "Java 프로그래밍"
        
        # 추가 문제 생성 (객관식으로 통일)
        result = question_generator_service.generate_question_with_rag(
            query=query,
            difficulty="보통",
            question_type="객관식"  # 객관식으로 통일
        )
        
        # 결과가 딕셔너리인 경우 처리
        if isinstance(result, dict):
            if result.get("success", False):
                question = result.get("question", "추가 문제가 생성되었습니다.")
                options = result.get("options", [])
                
                # 객관식만 허용 - 선택지가 없으면 오류
                if options and len(options) > 0:
                    content = f"{question}\n\n"
                    for i, option in enumerate(options, 1):
                        content += f"{i}. {option}\n"
                    print(f"✅ 추가 문제 - 선택지 포함된 문제 생성 완료")
                else:
                    print(f"❌ 추가 문제 - 선택지가 없어 객관식 생성 실패")
                    content = "죄송합니다. 객관식 문제 생성에 실패했습니다. 다시 시도해주세요."
            else:
                content = result.get("message", "추가 문제 생성에 실패했습니다.")
        else:
            # 문자열인 경우 그대로 사용
            content = str(result)
        
        # 최종 응답에서 정답 정보 제거
        import re
        final_content = re.sub(r'\[정답 정보:.*?\]', '', content, flags=re.DOTALL).strip()
        final_content = re.sub(r'정답 정보:.*?$', '', final_content, flags=re.DOTALL).strip()
        final_content = re.sub(r'\[정답.*?\]', '', final_content, flags=re.DOTALL).strip()
        final_content = re.sub(r'정답.*?$', '', final_content, flags=re.DOTALL).strip()

        # 마크다운 코드 블록 제거
        final_content = final_content.replace('```', '')

        print(f"🔍 최종 응답 content: {final_content}")
        
        # 추가 문제에서도 필수 필드들 포함
        domain = "Java Programming"
        concept = query[:200]  # 200자로 제한
        
        # 추가 문제의 정답 정보도 저장
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
            content=final_content,
            messageType="TEXT",
            sender="AI",
            chatState=user.chatState,
            domain=domain,
            concept=concept,
            problemText=problem_text,
            correctAnswer=correct_answer
        )
    except Exception as e:
        print(f"❌ 추가 문제 생성 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"추가 문제 생성 중 오류가 발생했습니다: {str(e)}")
