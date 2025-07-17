import os
import re
import tempfile

import fitz  # PyMuPDF
import streamlit as st

def clean_java_text(text):
    """Java 관련 텍스트를 정리하는 함수"""
    
    patterns = [
        # 1. 예제 번호 복원
        (r'▼\s*예제\s+(\d+)\s*-\s*(\d+)\s*/\s*(\w+)\s*\.\s*j(?:ava)?\s*(?=\s|$|[^\w])', r'▼ 예제 \1-\2/\3.java'),
        (r'예제\s+(\d+)\s*-\s*(\d+)\s*/\s*(\w+)\s*\.\s*j(?:ava)?\s*(?=\s|$|[^\w])', r'예제 \1-\2/\3.java'),
        
        # 2. 파일명 패턴
        (r'(\w+)\s*\.\s*j(?:ava)?\s*(?=\s|$|[^\w])', r'\1.java'),
        
        # 3. 클래스명 복원
        (r'(\w+)Ex\s*\.\s*j(?:ava)?\s*(?=\s|$|[^\w])', r'\1Ex.java'),
        (r'(\w+)Test\s*\.\s*j(?:ava)?\s*(?=\s|$|[^\w])', r'\1Test.java'),
        
        # 4. 패키지명 복원
        (r'\bj\s*\.\s*util\b', r'java.util'),
        (r'\bj\s*\.\s*io\b', r'java.io'),
        (r'\bj\s*\.\s*awt\b', r'java.awt'),
        
        # 5. API 관련 복원
        (r'\bJ\s+API\b', r'Java API'),
        (r'\bJava\s+A\s*P\s*I\b', r'Java API'),
        
        # 6. 숫자와 하이픈 사이 공백 제거
        (r'(\d+)\s*-\s+(\d+)', r'\1-\2'),
        
        # 7. System.out 관련 복원
        (r'System\s*\.\s*o+u*t\s*\.\s*print', r'System.out.print'),
        (r'System\s*\.\s*o+u*t\s*\.\s*println', r'System.out.println'),
        
        # 8. Java 키워드 복원
        (r'\bf+o*a+t\b', r'float'),
        (r'\bi+n+t\b', r'int'),
        (r'\bd+o*u+b+l+e\b', r'double'),
        (r'\bc+h*a+r\b', r'char'),
        (r'\bb+o*o+l+e*a*n\b', r'boolean'),
        
        # 9. 한국어 외래어 표기
        (r'리져브드', r'리저브드'),
        (r'클라스', r'클래스'),
        (r'메소드', r'메서드'),
        
        # 10. 주석 관련 복원
        (r'/\s*/\s*', r'// '),
        (r'/\s*\*', r'/*'),
        (r'\*\s*/', r'*/'),
    ]
    
    cleaned = text
    
    for pattern, replacement in patterns:
        try:
            cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
        except Exception:
            continue
    
    # 공백 정리
    cleaned = re.sub(r'\n\s*\n\s*\n+', '\n\n', cleaned)
    cleaned = re.sub(r'[ \t]+', ' ', cleaned)
    cleaned = re.sub(r'^\s+', '', cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r'\s+$', '', cleaned, flags=re.MULTILINE)
    
    return cleaned

def extract_text_from_pdf(pdf_path):
    """PyMuPDF로 PDF에서 텍스트 추출"""
    doc = fitz.open(pdf_path)
    pages = []
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text()
        
        if text.strip():  # 빈 페이지가 아닌 경우만
            pages.append({
                'page_number': page_num + 1,
                'content': text,
                'word_count': len(text.split())
            })
    
    doc.close()
    return pages

def main():
    st.set_page_config(page_title="간단한 PDF Java 텍스트 정리기", page_icon="📚")
    
    st.title("📚 간단한 PDF Java 텍스트 정리기")
    st.write("**복잡한 설치 없이** PDF에서 텍스트를 추출하고 Java 관련 파일명을 정리합니다.")
    
    st.success("✅ **설치 필요 없음** - PyMuPDF만 사용하여 간단하게 작동합니다!")
    
    st.divider()

    # 사이드바
    with st.sidebar:
        st.header("🔧 자동 정리 규칙")
        
        st.subheader("📝 파일명 복원")
        st.code("""
예제 2- 1/VarEx.j → 예제 2-1/VarEx.java
OverfowEx.j → OverflowEx.java
TestClass.j → TestClass.java
        """, language="text")
        
        st.subheader("📦 패키지명 복원")
        st.code("""
j.util → java.util
J API → Java API
        """, language="text")
        
        st.subheader("🔧 일반 오타 복원")
        st.code("""
foat → float
System.out.print 복원
        """, language="text")

    # 설정 옵션
    col1, col2 = st.columns(2)
    
    with col1:
        enable_text_cleaning = st.checkbox(
            "🔧 Java 텍스트 자동 정리", 
            value=True,
            help="Java 관련 텍스트 자동 정리"
        )
    
    with col2:
        remove_ebook_text = st.checkbox(
            "🗑️ eBook 샘플 텍스트 제거",
            value=True,
            help="[ebook - 샘플] 관련 텍스트 자동 제거"
        )
    
    show_statistics = st.checkbox(
        "📊 상세 통계 표시",
        value=True,
        help="페이지별 통계 정보 표시"
    )

    # 파일 업로드
    st.subheader("📤 PDF 파일 업로드")
    pdf_file = st.file_uploader(
        "PDF 파일을 선택하세요",
        type="pdf",
        help="텍스트가 포함된 PDF 파일만 지원합니다"
    )

    if pdf_file is not None:
        # 파일 정보 표시
        st.info(f"📄 파일명: {pdf_file.name} ({pdf_file.size:,} bytes)")
        
        # 임시 파일 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(pdf_file.getvalue())
            tmp_file_path = tmp_file.name
        
        try:
            with st.spinner("📄 PDF 텍스트 추출 중..."):
                pages = extract_text_from_pdf(tmp_file_path)
            
            if not pages:
                st.error("❌ PDF에서 텍스트를 추출할 수 없습니다.")
                st.warning("**가능한 원인:**")
                st.markdown("""
                - 스캔된 이미지 PDF (OCR 필요)
                - 보호된 PDF
                - 텍스트가 포함되지 않은 PDF
                """)
                
                # 직접 입력 옵션
                st.subheader("📝 직접 텍스트 입력")
                direct_text = st.text_area(
                    "텍스트를 직접 입력하세요:",
                    height=200,
                    placeholder="예: 예제 2- 1/VarEx.j\nclass VarEx {\n    // Java 코드\n}"
                )
                
                if direct_text and st.button("🔧 텍스트 정리하기"):
                    pages = [{
                        'page_number': 1,
                        'content': direct_text,
                        'word_count': len(direct_text.split())
                    }]
                else:
                    return

            # 텍스트 정리
            total_changes = 0
            ebook_removals = 0
            
            if remove_ebook_text or enable_text_cleaning:
                with st.spinner("🔧 텍스트 정리 중..."):
                    for page in pages:
                        original_content = page['content']
                        
                        # eBook 샘플 텍스트 제거
                        if remove_ebook_text:
                            patterns_to_remove = [
                                # 1. 정확한 패턴
                                r"\[ebook\s*-\s*샘플\.\s*무료\s*공유\]\s*자\s*바\s*의\s*정석\s*4\s*판\s*Java\s*21\s*올컬러.*?seong\.namkung@gmail\.com",
                                
                                # 2. 더 유연한 패턴
                                r"\[ebook.*?샘플.*?무료.*?공유\].*?자바.*?정석.*?4.*?판.*?Java.*?21.*?seong\.namkung@gmail\.com",
                                
                                # 3. 이메일 주소만
                                r"seong\.namkung@gmail\.com",
                                
                                # 4. ebook 부분만
                                r"\[ebook.*?샘플.*?무료.*?공유\].*?자바.*?정석.*?",
                                
                                # 5. 출시 정보
                                r"2025\.\s*7\.\s*7\s*출시",
                                
                                # 6. 올컬러 정보
                                r"올컬러.*?2025",
                            ]
                            
                            content_before = page['content']
                            for pattern in patterns_to_remove:
                                page['content'] = re.sub(pattern, "", page['content'], flags=re.IGNORECASE | re.DOTALL)
                            
                            if content_before != page['content']:
                                ebook_removals += 1
                        
                        # Java 텍스트 정리
                        if enable_text_cleaning:
                            cleaned_content = clean_java_text(page['content'])
                            if cleaned_content != page['content']:
                                total_changes += 1
                            page['content'] = cleaned_content
                        
                        # 빈 줄 정리
                        page['content'] = re.sub(r'\n\s*\n\s*\n+', '\n\n', page['content'])
                        page['content'] = page['content'].strip()

            # 결과 표시
            st.success("✅ 텍스트 처리 완료!")
            
            # 통계 정보
            if show_statistics:
                st.subheader("📊 처리 결과")
                col1, col2, col3, col4 = st.columns(4)
                
                total_words = sum(page['word_count'] for page in pages)
                total_text = "\n".join([page['content'] for page in pages])
                java_count = len(re.findall(r'\w+\.java\b', total_text))
                
                col1.metric("📄 총 페이지", len(pages))
                col2.metric("📝 총 단어", f"{total_words:,}")
                col3.metric("☕ Java 파일", java_count)
                
                if enable_text_cleaning or remove_ebook_text:
                    changes_text = []
                    if enable_text_cleaning and total_changes > 0:
                        changes_text.append(f"Java 정리 {total_changes}개")
                    if remove_ebook_text and ebook_removals > 0:
                        changes_text.append(f"샘플 제거 {ebook_removals}개")
                    
                    if changes_text:
                        col4.metric("🔧 정리된 페이지", " | ".join(changes_text))
                    else:
                        col4.metric("🔧 정리된 페이지", "없음")

                # 예제 파일 미리보기
                example_matches = re.findall(r'예제\s+\d+-\d+/\w+\.java', total_text)
                if example_matches:
                    st.info(f"🎯 **발견된 예제 파일:** {', '.join(example_matches[:5])}")
                    if len(example_matches) > 5:
                        st.write(f"... 외 {len(example_matches) - 5}개")

            # 결과 탭
            tab1, tab2, tab3 = st.tabs(["📋 페이지별 보기", "📝 전체 텍스트", "💾 다운로드"])
            
            with tab1:
                st.subheader("📋 페이지별 텍스트")
                for page in pages:
                    with st.expander(f"📄 페이지 {page['page_number']} (단어: {page['word_count']:,}개)"):
                        # 이 페이지의 Java 파일 찾기
                        page_java_files = re.findall(r'\w+\.java\b', page['content'])
                        if page_java_files:
                            st.success(f"☕ **이 페이지의 Java 파일:** {', '.join(set(page_java_files))}")
                        
                        st.text_area(
                            f"페이지 {page['page_number']} 내용",
                            page['content'],
                            height=300,
                            key=f"page_{page['page_number']}"
                        )
            
            with tab2:
                st.subheader("📝 전체 문서 텍스트")
                full_text = "\n\n".join([
                    f"=== 페이지 {page['page_number']} ===\n{page['content']}"
                    for page in pages
                ])
                st.text_area("전체 텍스트", full_text, height=600)
            
            with tab3:
                st.subheader("💾 다운로드 및 통계")
                
                # 다운로드
                full_text_for_download = "\n\n".join([
                    f"=== 페이지 {page['page_number']} ===\n{page['content']}"
                    for page in pages
                ])
                
                st.download_button(
                    label="📥 정리된 텍스트 다운로드",
                    data=full_text_for_download,
                    file_name=f"cleaned_{pdf_file.name.replace('.pdf', '')}.txt",
                    mime="text/plain"
                )
                
                # 상세 통계
                st.subheader("📊 상세 통계")
                total_chars = len(full_text_for_download)
                total_lines = len(full_text_for_download.splitlines())
                
                st.write(f"- **총 페이지:** {len(pages)}")
                st.write(f"- **총 문자:** {total_chars:,}")
                st.write(f"- **총 단어:** {total_words:,}")
                st.write(f"- **총 줄:** {total_lines:,}")
                
                # Java 파일 목록
                if java_count > 0:
                    st.subheader("☕ Java 파일 목록")
                    java_files = re.findall(r'\w+\.java\b', total_text)
                    unique_java_files = list(set(java_files))
                    
                    for i, java_file in enumerate(unique_java_files[:20], 1):
                        st.write(f"{i}. {java_file}")
                    
                    if len(unique_java_files) > 20:
                        st.write(f"... 외 {len(unique_java_files) - 20}개")

        except Exception as e:
            st.error(f"❌ 오류가 발생했습니다: {e}")
            st.exception(e)
            
        finally:
            # 임시 파일 정리
            if os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)

if __name__ == '__main__':
    main()
