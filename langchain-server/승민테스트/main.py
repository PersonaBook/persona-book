import os
import re
import json
import tempfile
from collections import Counter
import difflib

import fitz  # PyMuPDF
import streamlit as st

# JSON 키워드 데이터
KEYWORDS_DATA = [
    {"word": "문자 집합", "pages": [82]},
    {"word": "문자열 결합", "pages": [55]},
    {"word": "문자열 리터럴", "pages": [55]},
    {"word": "문자열 배열", "pages": [230]},
    {"word": "문자열 비교", "pages": [134]},
    {"word": "문자형", "pages": [76]},
    {"word": "문장", "pages": [108]},
    {"word": "바이트", "pages": [65]},
    {"word": "반복 순환 패턴", "pages": [184]},
    {"word": "반복문", "pages": [180]},
    {"word": "반환값", "pages": [283]},
    {"word": "반환타입", "pages": [277]},
    {"word": "배열", "pages": [206]},
    {"word": "배열 섞기", "pages": [222]},
    {"word": "배열 카운팅", "pages": [228]},
    {"word": "배열의 길이", "pages": [211]},
    {"word": "배열의 복사", "pages": [216]},
    {"word": "배열의 생성", "pages": [207]},
    {"word": "배열의 요소", "pages": [208]},
    {"word": "배열의 인덱스", "pages": [208]},
    {"word": "배열의 초기화", "pages": [213]},
    {"word": "배열의 출력", "pages": [214]},
    {"word": "버블 정렬", "pages": [226]},
    {"word": "범위 주석", "pages": [33]},
    {"word": "변수", "pages": [40]},
    {"word": "변수 값교환", "pages": [43]},
    {"word": "변수 명명규칙", "pages": [45]},
    {"word": "변수 초기화", "pages": [41]},
    {"word": "변수 타입", "pages": [40, 47]},
    {"word": "스택 오버플로우", "pages": [298]},
    {"word": "식(expression)", "pages": [108]},
    {"word": "식별자", "pages": [45]},
    {"word": "실수형", "pages": [89]},
    {"word": "실수형 범위", "pages": [89]},
    {"word": "실수형 저장형식", "pages": [92]},
    {"word": "클래스", "pages": [255]},
    {"word": "객체", "pages": [255]},
    {"word": "메서드", "pages": [273]},
    {"word": "생성자", "pages": [315]},
    {"word": "상속", "pages": [350]},
    {"word": "다형성", "pages": [380]},
    {"word": "캡슐화", "pages": [290]},
    {"word": "인터페이스", "pages": [400]},
    {"word": "추상클래스", "pages": [370]},
    {"word": "예외처리", "pages": [450]},
    {"word": "컬렉션", "pages": [500]},
    {"word": "제네릭", "pages": [520]},
    {"word": "스레드", "pages": [600]},
    {"word": "람다", "pages": [650]},
    {"word": "스트림", "pages": [670]}
]

def search_keywords(query, exact_match=False):
    """키워드 검색 함수"""
    if not query.strip():
        return []
    
    query = query.strip().lower()
    results = []
    
    for item in KEYWORDS_DATA:
        word = item["word"].lower()
        
        if exact_match:
            if word == query:
                results.append(item)
        else:
            if query in word or word in query:
                results.append(item)
    
    # 정확도 순으로 정렬
    def sort_key(item):
        word = item["word"].lower()
        if word == query:
            return 0
        elif word.startswith(query):
            return 1
        elif word.endswith(query):
            return 2
        else:
            return 3
    
    results.sort(key=sort_key)
    return results

def get_similar_keywords(query, limit=10):
    """유사한 키워드 추천"""
    if not query.strip():
        return []
    
    query = query.strip().lower()
    similarities = []
    
    for item in KEYWORDS_DATA:
        word = item["word"].lower()
        ratio = difflib.SequenceMatcher(None, query, word).ratio()
        if ratio > 0.3:
            similarities.append((ratio, item))
    
    similarities.sort(key=lambda x: x[0], reverse=True)
    return [item for ratio, item in similarities[:limit]]

def find_pages_for_topic(topic, pages_data):
    """특정 토픽과 관련된 페이지 찾기"""
    if not topic.strip() or not pages_data:
        return []
    
    keyword_results = search_keywords(topic)
    related_page_numbers = set()
    
    for result in keyword_results:
        related_page_numbers.update(result["pages"])
    
    related_pages = []
    for page in pages_data:
        if page["page_number"] in related_page_numbers:
            related_pages.append(page)
    
    return sorted(related_pages, key=lambda x: x["page_number"])

def is_figure_or_table_block(text, x0, y0, x1, y1, page_width, page_height):
    """그림과 표를 감지하는 함수"""
    text_clean = text.strip().lower()
    
    # 키워드 감지
    figure_table_keywords = [
        r'그림\s*\d+', r'표\s*\d+', r'도표\s*\d+', r'차트\s*\d+',
        r'figure\s*\d+', r'table\s*\d+', r'chart\s*\d+',
        r'<그림\s*\d+>', r'<표\s*\d+>', r'\[그림\s*\d+\]', r'\[표\s*\d+\]'
    ]
    
    for pattern in figure_table_keywords:
        if re.search(pattern, text_clean):
            return True, f"키워드 감지: {pattern}"
    
    # 표 패턴 감지
    lines = text.split('\n')
    table_indicators = 0
    
    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue
        
        separators = line_clean.count('|') + line_clean.count('─') + line_clean.count('-') * 0.5
        if separators >= 3:
            table_indicators += 1
    
    if table_indicators >= 2:
        return True, f"표 패턴 감지: {table_indicators}개 지표"
    
    # 위치 기반 감지
    block_width = x1 - x0
    block_height = y1 - y0
    center_x = page_width / 2
    center_y = page_height / 2
    block_center_x = (x0 + x1) / 2
    block_center_y = (y0 + y1) / 2
    
    is_center_area = (abs(block_center_x - center_x) < page_width * 0.3 and 
                     abs(block_center_y - center_y) < page_height * 0.3)
    is_small_block = (block_width < page_width * 0.6 and block_height < page_height * 0.2)
    
    if is_center_area and is_small_block and len(text.strip()) < 200:
        return True, f"중앙 영역 작은 블록"
    
    return False, ""

def extract_text_from_pdf_enhanced(pdf_path):
    """PDF 텍스트 추출"""
    doc = fitz.open(pdf_path)
    pages = []
    total_blocks_removed = 0
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        page_rect = page.rect
        page_width = page_rect.width
        page_height = page_rect.height
        
        text_blocks = page.get_text("blocks")
        page_content = []
        page_word_count = 0
        page_blocks_removed = 0

        for i, block in enumerate(text_blocks):
            if len(block) >= 7 and block[6] == 0:  # 텍스트 블록만
                x0, y0, x1, y1, text, block_no, block_type = block
                
                is_figure_table, reason = is_figure_or_table_block(
                    text, x0, y0, x1, y1, page_width, page_height
                )
                
                if is_figure_table:
                    page_blocks_removed += 1
                    continue
                
                if text.strip():
                    page_content.append(text)
                    page_word_count += len(text.split())
        
        total_blocks_removed += page_blocks_removed
        
        if page_content:
            page_text = "\n".join(page_content)
            page_text = re.sub(r'\n\s*\n\s*\n+', '\n\n', page_text)
            page_text = page_text.strip()
            
            if page_text:
                pages.append({
                    'page_number': page_num + 1,
                    'content': page_text,
                    'word_count': page_word_count,
                    'quality_score': 85  # 기본값
                })
    
    doc.close()
    return pages, total_blocks_removed

def main():
    st.set_page_config(page_title="Java 교재 키워드 검색 도구", page_icon="☕")
    
    st.title("☕ Java 교재 키워드 검색 도구")
    st.write("PDF에서 그림/표를 제거하고 키워드로 빠른 검색이 가능합니다.")
    
    # 세션 상태 초기화
    if 'filtered_pages' not in st.session_state:
        st.session_state.filtered_pages = None
    if 'filter_keyword' not in st.session_state:
        st.session_state.filter_keyword = None
    
    # 사이드바
    with st.sidebar:
        st.header("🔍 키워드 빠른 검색")
        
        # 키워드 검색 (PDF 없이도 가능)
        search_query = st.text_input("키워드 검색", placeholder="예: 배열, 클래스, 메서드")
        exact_match = st.checkbox("정확히 일치", value=False)
        
        if search_query:
            search_results = search_keywords(search_query, exact_match)
            
            if search_results:
                st.success(f"🔍 {len(search_results)}개 키워드 발견")
                
                for result in search_results[:10]:
                    pages_str = ", ".join(map(str, result["pages"]))
                    st.write(f"📌 **{result['word']}**")
                    st.write(f"   페이지: {pages_str}")
                    st.write("---")
            else:
                st.warning("키워드를 찾을 수 없습니다.")
                
                # 유사한 키워드 추천
                similar = get_similar_keywords(search_query, 5)
                if similar:
                    st.write("💡 **비슷한 키워드:**")
                    for item in similar:
                        if st.button(f"🔄 {item['word']}", key=f"similar_{item['word']}"):
                            st.session_state.search_query = item['word']
                            st.rerun()
        
        st.divider()
        
        # 카테고리별 키워드
        st.subheader("📂 주요 카테고리")
        categories = {
            "배열": ["배열", "배열의 길이", "배열의 생성", "2차원 배열"],
            "클래스": ["클래스", "객체", "메서드", "생성자"],
            "변수": ["변수", "변수 타입", "변수 초기화"],
            "연산자": ["산술 연산자", "비교 연산자", "논리 연산자"],
            "제어문": ["반복문", "조건문", "분기문"]
        }
        
        for category, keywords in categories.items():
            if st.button(f"📁 {category}", key=f"cat_{category}"):
                # 해당 카테고리의 모든 키워드를 표시
                st.session_state.category_view = category

    st.divider()

    # 파일 업로드
    st.subheader("📤 PDF 파일 업로드")
    pdf_file = st.file_uploader("PDF 파일을 선택하세요", type="pdf")

    if pdf_file is not None:
        st.info(f"📄 파일명: {pdf_file.name}")
        
        # 임시 파일 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(pdf_file.getvalue())
            tmp_file_path = tmp_file.name
        
        try:
            with st.spinner("🗑️ PDF 처리 중..."):
                pages, total_removed = extract_text_from_pdf_enhanced(tmp_file_path)
            
            if not pages:
                st.error("❌ PDF에서 텍스트를 추출할 수 없습니다.")
                return

            st.success(f"✅ 처리 완료! {len(pages)}개 페이지, {total_removed}개 블록 제거됨")
            
            # 키워드 검색 (PDF 처리 후)
            st.subheader("🔍 키워드 검색")
            
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                main_search = st.text_input("검색할 키워드", placeholder="예: 배열, 반복문")
            with col2:
                exact = st.checkbox("정확 일치")
            with col3:
                if st.button("🔍 검색"):
                    if main_search:
                        results = search_keywords(main_search, exact)
                        if results:
                            related_pages = find_pages_for_topic(main_search, pages)
                            if related_pages:
                                st.session_state.filtered_pages = related_pages
                                st.session_state.filter_keyword = main_search
                                st.success(f"✅ {len(related_pages)}개 관련 페이지 발견!")
                            else:
                                st.warning("해당 키워드의 페이지가 PDF에 없습니다.")
                        else:
                            st.warning("키워드를 찾을 수 없습니다.")
            
            # 필터링된 페이지 표시
            display_pages = st.session_state.filtered_pages if st.session_state.filtered_pages else pages
            filter_keyword = st.session_state.filter_keyword
            
            if filter_keyword:
                st.info(f"🔍 '{filter_keyword}' 키워드로 필터링된 {len(display_pages)}개 페이지")
                if st.button("🔄 전체 페이지 보기"):
                    st.session_state.filtered_pages = None
                    st.session_state.filter_keyword = None
                    st.rerun()

            # 결과 탭
            tab1, tab2, tab3 = st.tabs(["📋 페이지별 내용", "📝 전체 텍스트", "💾 다운로드"])
            
            with tab1:
                st.subheader("📋 페이지별 내용")
                if filter_keyword:
                    st.info(f"🔍 '{filter_keyword}' 관련 페이지만 표시")
                
                for page in display_pages:
                    quality_score = page.get('quality_score', 0)
                    
                    with st.expander(f"📄 페이지 {page['page_number']} (단어: {page['word_count']:,}개)"):
                        # Java 파일 찾기
                        java_files = re.findall(r'\w+\.java\b', page['content'])
                        if java_files:
                            st.success(f"☕ **Java 파일:** {', '.join(set(java_files))}")
                        
                        # 내용 표시
                        content = page['content']
                        if filter_keyword:
                            # 간단한 하이라이트
                            content = re.sub(
                                f"({re.escape(filter_keyword)})", 
                                r"**\1**", 
                                content, 
                                flags=re.IGNORECASE
                            )
                        
                        st.text_area(
                            f"페이지 {page['page_number']} 내용",
                            content,
                            height=300,
                            key=f"page_{page['page_number']}"
                        )
            
            with tab2:
                st.subheader("📝 전체 텍스트")
                full_text = "\n\n".join([
                    f"=== 페이지 {page['page_number']} ===\n{page['content']}"
                    for page in display_pages
                ])
                st.text_area("전체 텍스트", full_text, height=600)
            
            with tab3:
                st.subheader("💾 다운로드")
                
                full_text_download = "\n\n".join([
                    f"=== 페이지 {page['page_number']} ===\n{page['content']}"
                    for page in display_pages
                ])
                
                filename = f"extracted_text_{pdf_file.name.replace('.pdf', '')}.txt"
                if filter_keyword:
                    filename = f"filtered_{filter_keyword}_{pdf_file.name.replace('.pdf', '')}.txt"
                
                st.download_button(
                    label="📥 텍스트 다운로드",
                    data=full_text_download,
                    file_name=filename,
                    mime="text/plain"
                )
                
                st.write(f"- **총 페이지:** {len(display_pages)}개")
                st.write(f"- **총 단어:** {sum(page['word_count'] for page in display_pages):,}개")
                if filter_keyword:
                    st.write(f"- **필터 키워드:** {filter_keyword}")

        except Exception as e:
            st.error(f"❌ 오류: {e}")
            
        finally:
            if os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)

    else:
        # PDF 없이도 키워드 검색 가능
        st.subheader("🔍 키워드 검색 (PDF 없이)")
        st.write("PDF를 업로드하지 않아도 키워드 검색이 가능합니다.")
        
        # 전체 키워드 목록
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**📂 주요 키워드:**")
            main_keywords = ["배열", "클래스", "메서드", "변수", "반복문", "조건문", "생성자", "상속"]
            for keyword in main_keywords:
                result = search_keywords(keyword, exact_match=True)
                if result:
                    pages_str = ", ".join(map(str, result[0]["pages"]))
                    st.write(f"• **{keyword}** → 페이지: {pages_str}")
        
        with col2:
            st.write("**🔍 검색 예시:**")
            st.code("""
            "배열" → 배열 관련 키워드 15개
            "클래스" → 클래스 관련 키워드 8개  
            "메서드" → 메서드 관련 키워드 6개
            "변수" → 변수 관련 키워드 10개
            """)

if __name__ == '__main__':
    main()