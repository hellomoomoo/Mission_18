# 영화 리뷰 및 데이터를 JSON 파일로 저장하고 불러오는 기능

import json
from typing import List, Optional
from datetime import datetime
from models import Movie, Review

# JSON 파일 경로
MOVIES_FILE = 'movies.json'
REVIEWS_FILE = 'reviews.json'

# ---유틸리티 함수---

# JSON 파일에서 데이터 로드
def load_data(filepath: str) -> List[dict]:    
    try:
        with open(filepath, "r", encoding='utf-8') as f:
            return json.load(f)
        
    except FileNotFoundError:
        return []  # 파일이 없으면 빈 리스트 반환
    
# 데이터를 JSON 파일에 저장    
def save_data(filepath: str, data: List[dict]):
    with open(filepath, "w", encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        # json.dump()는 파이썬 객체를 JSON 문자열로 변환 후 저장하는 함수

# ---영화 데이터 함수---

# 모든 영화 목록 조회
def get_all_movies() -> List[Movie]:
    data = load_data(MOVIES_FILE)
    return [Movie(**item) for item in data]  # 리스트로 반환

# 영화 ID로 조회
def get_movie_by_id(movie_id: int) -> Optional[Movie]:
    data = load_data(MOVIES_FILE)
    for movie in data:
        if movie.get("id") == movie_id:
            return Movie(**movie)
    return None

# 새로운 영화 등록
def add_movie(movie: Movie) -> Movie:
    data = load_data(MOVIES_FILE)  # 기존 영화 리스트 불러오기

    # ID 자동 생성 (기존 영화가 있으면 가장 큰 ID + 1, 없으면 1)
    if data:
        movie.id = max(item["id"] for item in data) + 1
    else: 
        movie.id = 1

    # 새 영화를 리스트에 추가 후 저장
    data.append(movie.model_dump())
    save_data(MOVIES_FILE, data)
    return movie

# 영화 삭제
def delete_movie(movie_id: int) -> bool:
    data = load_data(MOVIES_FILE)  # 기존 영화 리스트 불러오기
    original_length = len(data)

    # 해당 ID가 아닌 영화들만 남겨놓기 (필터링)
    data = [movie for movie in data if movie["id"] != movie_id]
    
    # 실제로 삭제되었는지 확인 (리스트 길이가 줄었으면 삭제 성공)
    if len(data) < original_length:
        save_data(MOVIES_FILE, data)
        return True
    return False

# ---리뷰 관련 함수---

# 모든 리뷰 조회
def get_all_reviews() -> List[Review]:
    data = load_data(REVIEWS_FILE)
    return [Review(**review) for review in data]  # 대소문자 수정

# 특정 영화 리뷰 조회
def get_reviews_by_movie(movie_id: int) -> List[Review]:
    reviews = load_data(REVIEWS_FILE)
    # 해당 영화 ID와 일치하는 리뷰만 필터링
    movie_reviews = [r for r in reviews if r["movie_id"] == movie_id]
    return [Review(**review) for review in movie_reviews]

# 새 리뷰 등록
def create_review(review: Review) -> Review:
    reviews = load_data(REVIEWS_FILE)

    # ID 자동 생성
    if reviews:
        review.id = max(r["id"] for r in reviews) + 1
    else:
        review.id = 1

    # 작성 시간 자동 생성
    review.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    reviews.append(review.model_dump())
    save_data(REVIEWS_FILE, reviews)
    return review 

# 특정 리뷰 삭제
def delete_review(review_id: int) -> bool:
    reviews = load_data(REVIEWS_FILE)
    original_length = len(reviews)
    
    # 해당 ID가 아닌 리뷰들만 남기기
    reviews = [r for r in reviews if r["id"] != review_id]
    
    if len(reviews) < original_length:
        save_data(REVIEWS_FILE, reviews)
        return True
    return False

# 특정 영화의 평균 감성 점수 계산
def get_average_sentiment(movie_id: int) -> Optional[float]:
    reviews = get_reviews_by_movie(movie_id)
    
    # sentiment_score가 있는 리뷰만 필터링
    scores = [r.sentiment_score for r in reviews if r.sentiment_score is not None]
    
    if not scores:
        return None
    
    return sum(scores) / len(scores)