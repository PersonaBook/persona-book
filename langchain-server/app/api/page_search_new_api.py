"""
페이지 검색 관련 API
"""
from app.schemas.request.chat import UserMessageRequest
from app.schemas.response.chat import AiMessageResponse
from app.schemas.enum import ChatState
from app.services.question_generator_service import question_generator_service
from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.post("/waiting-keyword-for-page-search", response_model=AiMessageResponse)
def handle_waiting_keyword_for_page_search(user: UserMessageRequest):
    """페이지 검색 키워드 대기 처리"""
    try:
        print(f"🚀 페이지 검색 키워드 API 호출됨")
        print(f"📊 검색 키워드: {user.content}")
        
        keyword = user.content if user.content else ""
        
        if not keyword:
            return AiMessageResponse(
                userId=user.userId,
                bookId=user.bookId,
                content="검색하고 싶은 키워드를 입력해주세요.",
                messageType="TEXT",
                sender="AI",
                chatState=ChatState.WAITING_KEYWORD_FOR_PAGE_SEARCH,
            )
        
        # 페이지 검색 로직
        search_result = f"'{keyword}'에 대한 검색 결과를 찾았습니다."
        
        return AiMessageResponse(
            userId=user.userId,
            bookId=user.bookId,
            content=search_result,
            messageType="TEXT",
            sender="AI",
            chatState=ChatState.WAITING_KEYWORD_FOR_PAGE_SEARCH,
        )
    except Exception as e:
        print(f"❌ 페이지 검색 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"페이지 검색 중 오류가 발생했습니다: {str(e)}")


@router.post("/processing-page-search-result", response_model=AiMessageResponse)
def handle_processing_page_search_result(user: UserMessageRequest):
    """페이지 검색 결과 처리"""
    try:
        print(f"🚀 페이지 검색 결과 처리 API 호출됨")
        print(f"📊 검색 쿼리: {user.content}")
        
        search_query = user.content if user.content else ""
        
        if not search_query:
            return AiMessageResponse(
                userId=user.userId,
                bookId=user.bookId,
                content="검색할 내용을 입력해주세요.",
                messageType="TEXT",
                sender="AI",
                chatState=ChatState.PROCESSING_PAGE_SEARCH_RESULT,
            )
        
        # 키워드 기반 페이지 검색 (향상된 키워드 시스템 활용)
        try:
            from app.utils.chapter_mapper import load_keywords_data
            from app.data.keywords_detailed import keywords_data  # 실제 키워드 데이터
            
            keywords_data = load_keywords_data()
            search_results = []
            
            # 키워드와 매칭되는 페이지 찾기
            if 'chapters' in keywords_data:
                for chapter_id, chapter_info in keywords_data['chapters'].items():
                    chapter_keywords = chapter_info.get('keywords', [])
                    if any(search_query.lower() in keyword.lower() for keyword in chapter_keywords):
                        page_range = chapter_info.get('page_range', [])
                        search_results.append({
                            'chapter': chapter_id,
                            'title': chapter_info.get('title', f'챕터 {chapter_id}'),
                            'pages': f"{page_range[0]}-{page_range[1]}" if len(page_range) == 2 else "페이지 정보 없음"
                        })
            
            # 상세 키워드 데이터에서도 찾기
            try:
                import json
                import os
                detailed_keywords_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'keywords_detailed.json')
                with open(detailed_keywords_path, 'r', encoding='utf-8') as f:
                    detailed_keywords = json.load(f)
                
                exact_matches = []
                for item in detailed_keywords:
                    if search_query.lower() in item['word'].lower():
                        pages = item['pages']
                        exact_matches.append({
                            'keyword': item['word'],
                            'pages': ', '.join(map(str, pages))
                        })
                
                if exact_matches:
                    result_content = f"'{search_query}'에 대한 검색 결과를 찾았습니다:\n\n"
                    
                    # 정확한 키워드 매치 표시
                    result_content += "**정확한 키워드 매치:**\n"
                    for match in exact_matches[:5]:  # 최대 5개만 표시
                        result_content += f"• '{match['keyword']}' - 페이지: {match['pages']}\n"
                    
                    # 관련 챕터 표시
                    if search_results:
                        result_content += "\n**관련 챕터:**\n"
                        for result in search_results[:3]:  # 최대 3개 챕터
                            result_content += f"• {result['title']} (페이지 {result['pages']})\n"
                else:
                    result_content = f"'{search_query}'와 정확히 일치하는 키워드를 찾지 못했습니다."
                    if search_results:
                        result_content += "\n\n**유사한 내용이 포함된 챕터:**\n"
                        for result in search_results:
                            result_content += f"• {result['title']} (페이지 {result['pages']})\n"
                            
            except Exception as e:
                print(f"⚠️ 상세 키워드 검색 오류: {e}")
                if search_results:
                    result_content = f"'{search_query}'와 관련된 챕터를 찾았습니다:\n\n"
                    for result in search_results:
                        result_content += f"• {result['title']} (페이지 {result['pages']})\n"
                else:
                    result_content = f"'{search_query}'에 대한 관련 내용을 찾지 못했습니다."
                    
        except Exception as e:
            print(f"❌ 페이지 검색 오류: {e}")
            result_content = "페이지 검색 중 오류가 발생했습니다."
        
        return AiMessageResponse(
            userId=user.userId,
            bookId=user.bookId,
            content=result_content,
            messageType="TEXT",
            sender="AI",
            chatState=ChatState.PROCESSING_PAGE_SEARCH_RESULT,
        )
    except Exception as e:
        print(f"❌ 검색 결과 처리 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"검색 결과 처리 중 오류가 발생했습니다: {str(e)}")