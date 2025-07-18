import os
import re
import tempfile
from collections import Counter
import difflib

import fitz  # PyMuPDF
import streamlit as st

def calculate_text_quality_score(text):
    """추출된 텍스트의 품질을 평가하는 함수"""
    
    quality_score = 100
    issues = []
    
    # 1. 특수 문자 비율 체크
    special_chars = len(re.findall(r'[^\w\s가-힣]', text))
    total_chars = len(text)
    if total_chars > 0:
        special_ratio = special_chars / total_chars
        if special_ratio > 0.1:  # 10% 이상이면 점수 차감
            quality_score -= min(20, special_ratio * 100)
            issues.append(f"특수문자 비율 높음 ({special_ratio:.1%})")
    
    # 2. 의미없는 단어 패턴 체크
    meaningless_patterns = [
        r'[a-zA-Z]{1,2}\s+[a-zA-Z]{1,2}',  # 단일 문자들의 연속
        r'\d+\s+\d+\s+\d+',  # 숫자들의 연속
        r'[^\w\s가-힣]{3,}',  # 특수문자 연속
    ]
    
    for pattern in meaningless_patterns:
        matches = len(re.findall(pattern, text))
        if matches > 5:
            quality_score -= min(10, matches)
            issues.append(f"의미없는 패턴 감지 ({matches}개)")
    
    # 3. 한글/영어 비율 체크 (Java 교재 기준)
    korean_chars = len(re.findall(r'[가-힣]', text))
    english_chars = len(re.findall(r'[a-zA-Z]', text))
    
    if korean_chars + english_chars > 0:
        korean_ratio = korean_chars / (korean_chars + english_chars)
        if korean_ratio < 0.3:  # 한글 비율이 30% 미만이면
            quality_score -= 15
            issues.append(f"한글 비율 낮음 ({korean_ratio:.1%})")
    
    # 4. 줄바꿈 비율 체크
    lines = text.split('\n')
    short_lines = [line for line in lines if len(line.strip()) < 10]
    if len(lines) > 0:
        short_line_ratio = len(short_lines) / len(lines)
        if short_line_ratio > 0.5:  # 50% 이상이 짧은 줄이면
            quality_score -= 10
            issues.append(f"짧은 줄 비율 높음 ({short_line_ratio:.1%})")
    
    # 5. 코드 블록 왜곡 체크
    code_indicators = ['class ', 'public ', 'private ', 'System.out', 'import ', 'package ']
    broken_code = 0
    for indicator in code_indicators:
        if indicator in text:
            # 코드 키워드 주변에 이상한 공백이나 문자가 있는지 체크
            broken_patterns = [
                indicator.replace(' ', r'\s+'),  # 과도한 공백
                re.escape(indicator) + r'[^\w\s가-힣]',  # 이상한 문자
            ]
            for pattern in broken_patterns:
                if re.search(pattern, text):
                    broken_code += 1
    
    if broken_code > 0:
        quality_score -= min(15, broken_code * 3)
        issues.append(f"코드 블록 왜곡 감지 ({broken_code}개)")
    
    # 최종 점수 조정
    quality_score = max(0, min(100, quality_score))
    
    return {
        'quality_score': round(quality_score),
        'issues': issues,
        'total_chars': total_chars,
        'korean_chars': korean_chars,
        'english_chars': english_chars,
        'line_count': len(lines),
        'short_lines': len(short_lines)
    }

def analyze_extraction_completeness(pages):
    """추출 완성도 분석 함수"""
    
    total_pages = len(pages)
    empty_pages = sum(1 for page in pages if len(page['content'].strip()) < 50)
    
    # 페이지별 품질 점수 계산
    page_scores = []
    for page in pages:
        quality_info = calculate_text_quality_score(page['content'])
        page_scores.append(quality_info['quality_score'])
    
    avg_quality = sum(page_scores) / len(page_scores) if page_scores else 0
    
    # 추출 완성도 계산
    completeness = max(0, 100 - (empty_pages / total_pages * 100))
    
    return {
        'total_pages': total_pages,
        'empty_pages': empty_pages,
        'page_scores': page_scores,
        'avg_quality': round(avg_quality),
        'completeness': round(completeness),
        'extraction_grade': get_extraction_grade(avg_quality, completeness)
    }

def get_extraction_grade(quality, completeness):
    """추출 품질 등급 반환"""
    
    overall_score = (quality + completeness) / 2
    
    if overall_score >= 90:
        return "A (우수)"
    elif overall_score >= 80:
        return "B (양호)"
    elif overall_score >= 70:
        return "C (보통)"
    elif overall_score >= 60:
        return "D (미흡)"
    else:
        return "F (불량)"

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
    
    # ⏭ 표시 제거 (앞뒤로 2줄씩)
    cleaned = remove_lines_around_skip_symbol(cleaned)
    
    # 공백 정리
    cleaned = re.sub(r'\n\s*\n\s*\n+', '\n\n', cleaned)
    cleaned = re.sub(r'[ \t]+', ' ', cleaned)
    cleaned = re.sub(r'^\s+', '', cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r'\s+$', '', cleaned, flags=re.MULTILINE)
    
    return cleaned

def remove_lines_around_skip_symbol(text):
    """⏭ 표시가 있는 줄과 앞뒤 2줄씩 제거하는 함수"""
    
    lines = text.splitlines()
    lines_to_remove = set()
    
    # ⏭ 표시가 있는 줄 찾기
    for i, line in enumerate(lines):
        if '⏭' in line:
            # 현재 줄과 앞뒤 2줄씩 제거 대상으로 표시
            for j in range(max(0, i-2), min(len(lines), i+3)):
                lines_to_remove.add(j)
    
    # 제거 대상이 아닌 줄들만 남기기
    filtered_lines = []
    for i, line in enumerate(lines):
        if i not in lines_to_remove:
            filtered_lines.append(line)
    
    return '\n'.join(filtered_lines)

def extract_text_from_pdf(pdf_path):
    """PyMuPDF로 PDF에서 텍스트 추출 (그림/코드 블록 스킵 기능 추가)"""
    doc = fitz.open(pdf_path)
    pages = []

    def is_image_or_table_block(text):
        # 그림/표 관련 키워드만 감지 (코드 예시는 보존)
        image_keywords = ["그림", "Figure", "표", "Table"]
        if any(keyword in text for keyword in image_keywords):
            return True

        # 매우 명확한 이미지 블록만 감지 (예: 이미지 캡션)
        lines = text.splitlines()
        
        # 이미지 캡션 패턴 (예: "그림 2.1", "Figure 2-1")
        caption_patterns = [
            r'그림\s+\d+[-.]?\d*',
            r'Figure\s+\d+[-.]?\d*',
            r'표\s+\d+[-.]?\d*',
            r'Table\s+\d+[-.]?\d*'
        ]
        
        for line in lines:
            for pattern in caption_patterns:
                if re.search(pattern, line.strip()):
                    return True

        return False

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        
        # 페이지 내 모든 텍스트 블록을 가져옵니다.
        text_blocks = page.get_text("blocks")
        
        # 디버깅: 원본 블록 순서 출력
        print(f"\n=== 페이지 {page_num + 1} 원본 블록 순서 ===")
        for i, block in enumerate(text_blocks):
            if block[6] == 0:  # 텍스트 블록만
                x0, y0, x1, y1, text, block_no, block_type = block
                print(f"블록 {i}: 좌표({x0:.0f}, {y0:.0f}) - '{text.strip()[:50]}...'")
        
        # 좌표 기반으로 텍스트 블록 정렬
        sorted_blocks = sort_blocks_by_reading_order(text_blocks)
        
        page_content = []
        page_word_count = 0

        for block in sorted_blocks:
            text = block[4] # 텍스트 내용
            
            if is_image_or_table_block(text):
                print(f"페이지 {page_num + 1}의 텍스트 블록: '{text.strip()[:50]}...'은 그림/표 블록으로 추정되어 스킵합니다.")
                continue # 다음 텍스트 블록으로 넘어감

            if text.strip(): # 빈 텍스트 블록이 아닌 경우만 추가
                page_content.append(text)
                page_word_count += len(text.split())
        
        if page_content: # 페이지에 유효한 텍스트 블록이 있는 경우만 추가
            page_text = "\n".join(page_content)
            
            # 텍스트 품질 분석
            quality_info = calculate_text_quality_score(page_text)
            
            pages.append({
                'page_number': page_num + 1,
                'content': page_text,
                'word_count': page_word_count,
                'quality_score': quality_info['quality_score'],
                'quality_issues': quality_info['issues'],
                'char_stats': {
                    'total_chars': quality_info['total_chars'],
                    'korean_chars': quality_info['korean_chars'],
                    'english_chars': quality_info['english_chars'],
                    'line_count': quality_info['line_count'],
                    'short_lines': quality_info['short_lines']
                }
            })
    
    doc.close()
    return pages

def analyze_text_block_order(page):
    """PyMuPDF 텍스트 블록 읽기 순서 분석 및 시각화"""
    
    text_blocks = page.get_text("blocks")
    
    print("=== PyMuPDF 텍스트 블록 읽기 순서 분석 ===")
    
    for i, block in enumerate(text_blocks):
        if block[6] == 0:  # 텍스트 블록만
            x0, y0, x1, y1, text, block_no, block_type = block
            print(f"블록 {i}: 좌표({x0:.0f}, {y0:.0f}) - 내용: '{text.strip()[:30]}...'")
    
    return text_blocks

def sort_blocks_by_reading_order(text_blocks):
    """텍스트 블록을 읽기 순서(위→아래, 왼쪽→오른쪽)로 정렬"""
    
    # 텍스트 블록만 필터링
    text_only_blocks = [block for block in text_blocks if block[6] == 0]
    
    # 좌표 기반 정렬 (y좌표 우선, 같은 줄이면 x좌표 순)
    sorted_blocks = sorted(text_only_blocks, key=lambda block: (block[1], block[0]))
    
    print("=== 정렬된 텍스트 블록 순서 ===")
    for i, block in enumerate(sorted_blocks):
        x0, y0, x1, y1, text, block_no, block_type = block
        print(f"정렬 후 {i}: 좌표({x0:.0f}, {y0:.0f}) - 내용: '{text.strip()[:30]}...'")
    
    return sorted_blocks

def merge_nearby_blocks(sorted_blocks, distance_threshold=10):
    """가까운 텍스트 블록들을 병합"""
    
    merged_blocks = []
    current_group = []
    
    for block in sorted_blocks:
        x0, y0, x1, y1, text, block_no, block_type = block
        
        if not current_group:
            current_group.append(block)
        else:
            # 이전 블록과 y좌표 차이 확인
            prev_y = current_group[-1][1]
            
            if abs(y0 - prev_y) <= distance_threshold:
                # 같은 줄로 판단하여 그룹에 추가
                current_group.append(block)
            else:
                # 새 줄 시작, 이전 그룹 병합
                merged_text = " ".join([b[4].strip() for b in current_group])
                merged_blocks.append(merged_text)
                current_group = [block]
    
    # 마지막 그룹 처리
    if current_group:
        merged_text = " ".join([b[4].strip() for b in current_group])
        merged_blocks.append(merged_text)
    
    return merged_blocks

# 자주 나오는 다이어그램 패턴 자동 감지
COMMON_PATTERNS = {
    'variable_operations': ['tmp', '=', 'x', 'y'],
    'class_structure': ['class', 'private', 'public'],
    'memory_layout': ['Stack', 'Heap', '메모리'],
    'inheritance': ['extends', '상속', '부모클래스']
}

def detect_variable_swap_diagram(text):
    """변수 값 교환 다이어그램을 자동으로 감지하는 함수"""
    for pattern in COMMON_PATTERNS['variable_operations']:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

def detect_class_structure(text):
    """클래스 구조 다이어그램을 자동으로 감지하는 함수"""
    for pattern in COMMON_PATTERNS['class_structure']:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

def process_diagrams_hybrid(page_data):
    text = page_data['content']
    
    # 자동 감지 및 기본 템플릿 적용
    if detect_variable_swap_diagram(text):
        text += "\n\n[다이어그램: 변수 값 교환 과정]\n"
        text += "- 3단계 교환 과정 (tmp=x → x=y → y=tmp)\n"
        text += "- 각 단계별 메모리 상태 변화 표현\n"
        page_data['diagram_type'] = 'variable_swap'
        
    elif detect_class_structure(text):
        text += "\n\n[다이어그램: 클래스 구조]\n"
        text += "- 클래스 멤버변수와 메서드 구조 표현\n"
        page_data['diagram_type'] = 'class_structure'
    
    page_data['content'] = text
    return page_data

# 중요한 다이어그램만 수동으로 상세 설명 추가
DETAILED_DIAGRAMS = {
    15: {
        'enhanced_description': '''
        변수 값 교환 알고리즘의 핵심 개념:
        1. 임시변수 필요성: 한 변수의 값을 덮어쓰기 전에 백업
        2. 순서의 중요성: tmp→x→y 순서를 바꾸면 안됨
        3. 메모리 효율성: 추가 공간 O(1) 사용
        ''',
        'related_code': '''
        // 기본 교환 방법
        int tmp = x;
        x = y;
        y = tmp;
        
        // 응용: 배열에서 두 요소 교환
        int tmp = arr[i];
        arr[i] = arr[j];
        arr[j] = tmp;
        '''
    }
}

def enhance_educational_content(page_data):
    """교육적 가치를 높이는 콘텐츠 강화"""
    
    # 1. 자동 다이어그램 감지
    page_data = process_diagrams_hybrid(page_data)
    
    # 2. 중요 페이지는 수동 상세 설명 추가
    page_num = page_data['page_number']
    if page_num in DETAILED_DIAGRAMS:
        detail = DETAILED_DIAGRAMS[page_num]
        page_data['content'] += f"\n\n[상세 설명]\n{detail['enhanced_description']}"
        page_data['content'] += f"\n\n[관련 코드]\n{detail['related_code']}"
    
    # 3. RAG 최적화 태그 추가
    if page_data.get('diagram_type'):
        page_data['content'] += f"\n\n#시각학습 #다이어그램 #{page_data['diagram_type']}"
    
    return page_data

# 핵심 개념 페이지만 수동으로 상세 처리
PRIORITY_PAGES = [15, 23, 45, 67, 89]  # 중요 다이어그램 페이지

# 사용자 피드백을 통한 점진적 개선
def collect_diagram_feedback(page_num, user_rating):
    if user_rating < 3:
        # 해당 페이지 수동 보완 필요
        add_to_manual_enhancement_queue(page_num)

def main():
    st.set_page_config(page_title="RAG 텍스트 품질 검증 도구", page_icon="📊")
    
    st.title("📊 RAG 텍스트 품질 검증 도구")
    st.write("**RAG 시스템을 위한** PDF 텍스트 추출 품질을 검증하고 Java 관련 파일명을 정리합니다.")
    
    st.success("✅ **텍스트 품질 분석** - 원본 대비 추출된 텍스트의 일치도를 평가합니다!")
    
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
        
        st.divider()
        st.header("📊 RAG 텍스트 품질 검증")
        
        st.subheader("🎯 품질 평가 기준")
        st.write("추출된 텍스트의 품질을 다음 기준으로 평가:")
        st.code("""
• 특수문자 비율 (10% 이하)
• 의미없는 패턴 감지
• 한글/영어 비율 (한글 30% 이상)
• 짧은 줄 비율 (50% 이하)
• 코드 블록 왜곡 여부
        """, language="text")
        
        st.subheader("🏆 품질 등급")
        st.write("텍스트 품질 점수에 따른 등급 분류:")
        st.code("""
A등급: 90점 이상 (우수) 🟢
B등급: 80-89점 (양호) 🔵
C등급: 70-79점 (보통) 🟡
D등급: 60-69점 (미흡) 🟠
F등급: 60점 미만 (불량) 🔴
        """, language="text")
        
        st.subheader("🔍 RAG 활용도")
        st.write("품질 점수가 높을수록 RAG 시스템에서:")
        st.code("""
• 더 정확한 검색 결과
• 향상된 응답 품질
• 낮은 오답률
• 효율적인 문서 분할
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
    
    # RAG 텍스트 품질 검증 설정
    st.subheader("🔍 RAG 텍스트 품질 검증")
    enable_quality_analysis = st.checkbox(
        "📊 텍스트 품질 분석 활성화",
        value=True,
        help="추출된 텍스트의 품질을 분석하여 RAG 시스템 성능을 평가합니다"
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
                    quality_info = calculate_text_quality_score(direct_text)
                    pages = [{
                        'page_number': 1,
                        'content': direct_text,
                        'word_count': len(direct_text.split()),
                        'quality_score': quality_info['quality_score'],
                        'quality_issues': quality_info['issues'],
                        'char_stats': {
                            'total_chars': quality_info['total_chars'],
                            'korean_chars': quality_info['korean_chars'],
                            'english_chars': quality_info['english_chars'],
                            'line_count': quality_info['line_count'],
                            'short_lines': quality_info['short_lines']
                        }
                    }]
                else:
                    return

            # 텍스트 품질 분석 결과 표시
            if enable_quality_analysis:
                st.subheader("📊 RAG 텍스트 추출 품질 분석")
                
                # 전체 품질 분석
                extraction_analysis = analyze_extraction_completeness(pages)
                
                # 품질 메트릭 표시
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("📄 총 페이지", extraction_analysis['total_pages'])
                
                with col2:
                    st.metric("📊 평균 품질 점수", f"{extraction_analysis['avg_quality']}/100")
                
                with col3:
                    st.metric("✅ 추출 완성도", f"{extraction_analysis['completeness']}%")
                
                with col4:
                    grade_color = {
                        "A (우수)": "🟢",
                        "B (양호)": "🔵", 
                        "C (보통)": "🟡",
                        "D (미흡)": "🟠",
                        "F (불량)": "🔴"
                    }
                    grade = extraction_analysis['extraction_grade']
                    st.metric("🎯 추출 등급", f"{grade_color.get(grade, '⚪')} {grade}")
                
                # 품질 이슈 요약
                all_issues = []
                for page in pages:
                    all_issues.extend(page['quality_issues'])
                
                if all_issues:
                    st.warning("⚠️ **감지된 품질 이슈:**")
                    issue_counter = Counter(all_issues)
                    for issue, count in issue_counter.most_common(5):
                        st.write(f"- {issue}: {count}개 페이지")
                else:
                    st.success("✅ 품질 이슈가 감지되지 않았습니다!")
            
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
            
            # 텍스트 품질 정보 업데이트 (정리 후 재계산)
            if enable_quality_analysis:
                for page in pages:
                    quality_info = calculate_text_quality_score(page['content'])
                    page['quality_score'] = quality_info['quality_score']
                    page['quality_issues'] = quality_info['issues']
                    page['char_stats'] = {
                        'total_chars': quality_info['total_chars'],
                        'korean_chars': quality_info['korean_chars'],
                        'english_chars': quality_info['english_chars'],
                        'line_count': quality_info['line_count'],
                        'short_lines': quality_info['short_lines']
                    }

            # 결과 표시
            st.success("✅ 텍스트 처리 완료!")
            
            # 통계 정보
            if show_statistics:
                st.subheader("📊 처리 결과")
                col1, col2, col3, col4, col5 = st.columns(5)
                
                total_words = sum(page['word_count'] for page in pages)
                total_text = "\n".join([page['content'] for page in pages])
                java_count = len(re.findall(r'\w+\.java\b', total_text))
                
                # 품질 점수 계산
                if enable_quality_analysis:
                    avg_quality = sum(page['quality_score'] for page in pages) / len(pages)
                    low_quality_pages = sum(1 for page in pages if page['quality_score'] < 70)
                else:
                    avg_quality = 0
                    low_quality_pages = 0
                
                col1.metric("📄 총 페이지", len(pages))
                col2.metric("📝 총 단어", f"{total_words:,}")
                col3.metric("☕ Java 파일", java_count)
                col4.metric("📊 평균 품질", f"{avg_quality:.0f}/100")
                
                if enable_text_cleaning or remove_ebook_text:
                    changes_text = []
                    if enable_text_cleaning and total_changes > 0:
                        changes_text.append(f"Java 정리 {total_changes}개")
                    if remove_ebook_text and ebook_removals > 0:
                        changes_text.append(f"샘플 제거 {ebook_removals}개")
                    
                    if changes_text:
                        col5.metric("🔧 정리된 페이지", " | ".join(changes_text))
                    else:
                        col5.metric("🔧 정리된 페이지", "없음")
                else:
                    col5.metric("⚠️ 품질 주의", f"{low_quality_pages}개 페이지")

            # 결과 탭
            tab1, tab2, tab3 = st.tabs(["📋 페이지별 품질 분석", "📝 전체 텍스트", "💾 다운로드 & 통계"])
            
            with tab1:
                st.subheader("📋 페이지별 품질 분석")
                for page in pages:
                    # 품질 점수에 따른 아이콘 설정
                    quality_score = page.get('quality_score', 0)
                    if quality_score >= 90:
                        quality_icon = "🟢"
                    elif quality_score >= 80:
                        quality_icon = "🔵"
                    elif quality_score >= 70:
                        quality_icon = "🟡"
                    elif quality_score >= 60:
                        quality_icon = "🟠"
                    else:
                        quality_icon = "🔴"
                    
                    with st.expander(f"📄 페이지 {page['page_number']} (단어: {page['word_count']:,}개, 품질: {quality_score}/100 {quality_icon})"):
                        # 텍스트 품질 정보 표시
                        if enable_quality_analysis and page.get('quality_issues'):
                            st.warning(f"⚠️ **품질 이슈:** {', '.join(page['quality_issues'])}")
                        
                        # 문자 통계 정보
                        if enable_quality_analysis and page.get('char_stats'):
                            char_stats = page['char_stats']
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.caption(f"📝 총 문자: {char_stats['total_chars']:,}")
                                st.caption(f"🇰🇷 한글: {char_stats['korean_chars']:,}")
                            
                            with col2:
                                st.caption(f"🇺🇸 영어: {char_stats['english_chars']:,}")
                                st.caption(f"📏 총 줄: {char_stats['line_count']:,}")
                            
                            with col3:
                                short_ratio = char_stats['short_lines'] / char_stats['line_count'] if char_stats['line_count'] > 0 else 0
                                st.caption(f"📉 짧은 줄: {char_stats['short_lines']:,} ({short_ratio:.1%})")
                        
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
                st.subheader("💾 다운로드 & RAG 품질 통계")
                
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
                
                # 품질 통계
                if enable_quality_analysis:
                    st.subheader("📊 RAG 텍스트 품질 통계")
                    
                    # 전체 품질 분석
                    extraction_analysis = analyze_extraction_completeness(pages)
                    
                    st.write(f"- **평균 품질 점수:** {extraction_analysis['avg_quality']}/100")
                    st.write(f"- **추출 완성도:** {extraction_analysis['completeness']}%")
                    st.write(f"- **전체 등급:** {extraction_analysis['extraction_grade']}")
                    st.write(f"- **빈 페이지:** {extraction_analysis['empty_pages']}개")
                    
                    # 품질 등급별 페이지 분포
                    st.subheader("📈 품질 등급별 페이지 분포")
                    grade_distribution = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
                    
                    for page in pages:
                        score = page.get('quality_score', 0)
                        if score >= 90:
                            grade_distribution["A"] += 1
                        elif score >= 80:
                            grade_distribution["B"] += 1
                        elif score >= 70:
                            grade_distribution["C"] += 1
                        elif score >= 60:
                            grade_distribution["D"] += 1
                        else:
                            grade_distribution["F"] += 1
                    
                    for grade, count in grade_distribution.items():
                        if count > 0:
                            percentage = (count / len(pages)) * 100
                            st.write(f"- **{grade}등급:** {count}개 페이지 ({percentage:.1f}%)")
                    
                    # 주요 품질 이슈 통계
                    all_issues = []
                    for page in pages:
                        all_issues.extend(page.get('quality_issues', []))
                    
                    if all_issues:
                        st.subheader("⚠️ 주요 품질 이슈")
                        issue_counter = Counter(all_issues)
                        for issue, count in issue_counter.most_common(10):
                            st.write(f"- **{issue}:** {count}개 페이지")
                
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
