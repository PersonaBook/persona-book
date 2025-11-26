import logging
import sys
from pathlib import Path
from app.core.config import settings


def setup_logging():
    """애플리케이션 로깅 설정"""
    log_level = logging.DEBUG if settings.debug else logging.INFO
    
    # 포맷터 생성
    detailed_formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        fmt='%(levelname)s - %(message)s'
    )
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(simple_formatter if settings.debug else detailed_formatter)
    
    # 파일 핸들러 (프로덕션 환경에서만)
    handlers = [console_handler]
    if settings.app_env == "production":
        log_dir = Path(__file__).resolve().parent.parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)
        file_handler = logging.FileHandler(log_dir / "app.log")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(detailed_formatter)
        handlers.append(file_handler)
    
    # 루트 로거 설정
    logging.basicConfig(
        level=log_level,
        handlers=handlers
    )
    
    # 서드파티 라이브러리 로거는 WARNING 레벨로 설정하여 노이즈 감소
    logging.getLogger("elasticsearch").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    

def get_logger(name: str) -> logging.Logger:
    """모듈용 로거 인스턴스 가져오기"""
    return logging.getLogger(name)
