"""
캐싱 서비스 - PDF 처리 결과를 메모리에 저장
"""
import os
import pickle
from typing import List, Optional
from langchain.schema import Document


class CacheService:
    """PDF 처리 결과를 캐싱하는 서비스"""
    
    def __init__(self):
        self.cache_dir = "./cache"
        self.ensure_cache_dir()
    
    def ensure_cache_dir(self):
        """캐시 디렉토리 생성"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def get_cache_key(self, pdf_path: str, max_pages: Optional[int] = None) -> str:
        """캐시 키 생성"""
        file_stat = os.stat(pdf_path)
        key_parts = [
            os.path.basename(pdf_path),
            str(file_stat.st_mtime),  # 파일 수정 시간
            str(max_pages) if max_pages else "all"
        ]
        return "_".join(key_parts) + ".pkl"
    
    def get_cached_chunks(self, pdf_path: str, max_pages: Optional[int] = None) -> Optional[List[Document]]:
        """캐시된 청크 가져오기"""
        cache_key = self.get_cache_key(pdf_path, max_pages)
        cache_path = os.path.join(self.cache_dir, cache_key)
        
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'rb') as f:
                    chunks = pickle.load(f)
                print(f"✅ 캐시에서 청크 로드: {len(chunks)}개")
                return chunks
            except Exception as e:
                print(f"❌ 캐시 로드 실패: {e}")
        
        return None
    
    def cache_chunks(self, pdf_path: str, chunks: List[Document], max_pages: Optional[int] = None):
        """청크를 캐시에 저장"""
        cache_key = self.get_cache_key(pdf_path, max_pages)
        cache_path = os.path.join(self.cache_dir, cache_key)
        
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(chunks, f)
            print(f"✅ 청크 캐시 저장: {len(chunks)}개")
        except Exception as e:
            print(f"❌ 캐시 저장 실패: {e}")


# 싱글톤 인스턴스
cache_service = CacheService() 