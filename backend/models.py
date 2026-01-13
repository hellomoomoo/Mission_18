# 데이터 구조 설계 부분
# 리뷰 데이터 형태 정의

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# 영화 데이터 모델
class Movie(BaseModel):   # Pydantic이 상속받아 데이터 검증 및 직렬화 지원
    id: Optional[int] = None  # 영화 고유 ID (자동 생성)
    title: str                 # 영화 제목
    release_date: str          # 개봉일 (예: "2024-01-15")
    director: str              # 감독 이름
    genre: str                 # 장르 (예: "액션", "드라마")
    poster_url: str            # 포스터 이미지 URL
# 참고로 Optional은 선택적 필드 Optional[int]라고 dtype을 명시해서 잘못된 형식이 들어오면 FastAPI가 알아서 검증


# 리뷰 데이터 모델 (심화)
class Review(BaseModel):
    id: Optional[int] = None       # 리뷰 고유 ID (자동 생성)
    movie_id: int                  # 어떤 영화에 대한 리뷰인지
    author: str                    # 작성자 이름
    content: str                   # 리뷰 내용
    sentiment_score: Optional[float] = None  # 감성 분석 점수 (0~1, 나중에 추가)
    created_at: Optional[str] = None  # 작성 시간 (자동 생성)