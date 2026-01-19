# FastAPI 서버

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from models import Movie, Review
import database as db
import sentiment as sentiment_analyzer

# FastAPI 앱 생성

app = FastAPI(
    title="Movie Revire API",
    description="영화 정보 및 리뷰를 관리하는 API",
    version="1.0.0"
)

# CORS 설정: 다른 도메인(Streamlit 같은 프론트엔드)에서 이 API를 호출할 수 있도록 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     # 모든 출처 허용 / 배포시에는 특정 도메인만 허용 권장
    allow_credentials=True,
    allow_methods=["*"],    # 모든 HTTP 메소드 허용 (GET, POST, DELETE 등)
    allow_headers=["*"],    # 모든 헤더 허용
)

# ---기본 엔드포인트---

# 모든 영화 목록 조회
@app.get("/movies", response_model=List[Movie])
def get_movies():
    """
    GET http://localhost:8000/movies
    """
    movies = db.get_all_movies()
    return movies

# 특정 영화 상세 조회
@app.get("/movies/{movie_id}", response_model=Movie)
def get_movie(movie_id: int):
    """
    GET http://localhost:8000/movies/1
    """
    movie = db.get_movie_by_id(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="영화를 찾을 수 없습니다.")
    return movie

# 새로운 영화 등록
@app.post("/movies", response_model=Movie)
def create_movie(movie: Movie):
    """

    POST http://localhost:8000/movies

    Request Body 예시:
    {
        "title": "인터스텔라",
        "release_data": "2014-11-06",
        "director": "크리스토퍼 놀란",
        "genre": "SF",
        "poster_url": "https://example.com/poster.jpg"
    }

    Args:
        movie: Movie 객체 (id는 자동 생성되므로 보내지 않아도 됨)
        
    Returns:
        생성된 Movie 객체 (id 포함)

    """

    new_movie = db.add_movie(movie)
    return new_movie

# 영화 삭제 - 디버깅(관련 리뷰도 함께 삭제하도록 로직 추가)
@app.delete("/movies/{movie_id}")
def delete_movie(movie_id: int):
    """
    DELETE http://localhost:8000/movies/1

    Args:
        movie_id: 삭제할 영화 ID

    Returns:
        삭제 성공 메시지

    Rasies:
        HTTPException(404): 해당 ID의 영화 없는 경우
    """

    success = db.delete_movie(movie_id)
    if not success:
        raise HTTPException(status_code=404, detail="영화를 찾을 수 없습니다.")
    
    # 해당 영화의 모든 리뷰도 함께 삭제
    reviews = db.load_data(db.REVIEWS_FILE)
    original_count = len(reviews)
    reviews = [r for r in reviews if r["movie_id"] != movie_id]
    deleted_reviews = original_count - len(reviews)
    db.save_data(db.REVIEWS_FILE, reviews)

    return {
        "message": f"영화가 삭제되었습니다. (리뷰 {deleted_reviews}개도 함께 삭제됨)",
        "deleted_reviews": deleted_reviews
    }

# 영화 정보 수정
@app.put("/movies/{movie_id}", response_model=Movie)
def update_movie(movie_id: int, movie: Movie):
    """
    PUT http://localhost:8000/movies/1
    
    Args:
        movie_id: 수정할 영화 ID
        movie: 수정할 영화 정보
        
    Returns:
        수정된 Movie 객체
    """

    # 기존 영화 확인
    existing_movie = db.get_movie_by_id(movie_id)
    if not existing_movie:
        raise HTTPException(status_code=404, detail="영화를 찾을 수 없습니다.")
    
    # ID 유지 (요청 body의 id는 무시하고 URL의 movie_id 사용)
    movie.id = movie_id
    
    # 데이터 업데이트
    data = db.load_data(db.MOVIES_FILE)
    for i, m in enumerate(data):
        if m["id"] == movie_id:
            data[i] = movie.model_dump()
            break

    db.save_data(db.MOVIES_FILE, data)
    return movie


# --- 리뷰 관련 엔드포인트 ---

# 모든 리뷰 조회
@app.get("/reviews", response_model=List[Review])
def get_all_reviews():
    """
    GET http://localhost:8000/reviews
    """

    reviews = db.get_all_reviews()
    return reviews

# 특정 영화 모든 리뷰 조회
@app.get("/movies/{movie_id}/reviews", response_model=List[Review])
def get_movie_reviews(movie_id: int):
    """
    GET http://localhost:8000/movies/1/reviews

    Args:
        movie_id: 리뷰 조회할 영화 ID

    Returns:
        Review 객체 리스트
    """

    reviews = db.get_reviews_by_movie(movie_id)
    return reviews

# 새로운 리뷰 작성(감성 분석 자동 추가 - 디버깅)
@app.post("/reviews", response_model=Review)
def create_review(review: Review):
    """
    POST http://localhost:8000/reviews

    Request Body 예시:
    {
        "movie_id": 1,
        "author": "무무",
        "content": "정말 감동적인 영화였습니다!"
    }
    
    Args:
        review: Review 객체 (id, sentiment_score, created_at은 자동 생성)
        
    Returns:
        생성된 Review 객체 (id, 작성시간 포함)
        
    Note:
        sentiment_score는 리뷰 작성 시 자동으로 감성 분석되어 저장됨 ( 0~1 사이 값 )
    """
    # 영화가 존재하는지 확인
    movie = db.get_movie_by_id(review.movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="해당 영화를 찾을 수 없습니다. 영화 ID를 다시 한 번 확인해주세요.")
    
    # 감성 분석 자동 추가 - 디버깅
    if review.content:
        review.sentiment_score = sentiment_analyzer.analyze_sentiment(review.content)

    new_review = db.create_review(review)
    return new_review

# 리뷰 삭제
@app.delete("/reviews/{review_id}")
def delete_review(review_id: int):
    """
    DELETE http://localhost:8000/reviews/1
    
    Args:
        review_id: 삭제할 리뷰의 ID
        
    Returns:
        삭제 성공 메시지
        
    Raises:
        HTTPException(404): 해당 ID의 리뷰가 없을 때
    """

    success = db.delete_review(review_id)
    if not success:
        raise HTTPException(status_code=404, detail="리뷰를 찾을 수 없습니다. 영화 ID를 다시 한 번 확인해주세요.")
    return {"message": "리뷰가 삭제되었습니다."}

# 특정 영화의 평균 감성 점수 조회
@app.get("/movies/{movie_id}/sentiment")
def get_movie_sentiment(movie_id: int):
    """
    GET http://localhost:8000/movies/1/sentiment
    
    Args:
        movie_id: 감성 점수를 조회할 영화의 ID
        
    Returns:
        평균 감성 점수 (0~1 사이 값)
        
    Note:
        리뷰가 없거나 감성 분석이 안된 경우 None 반환
    """

    avg_score = db.get_average_sentiment(movie_id)
    if avg_score is None:
        return {"movie_id": movie_id, "average_sentiment": None, "message": "감성 분석 데이터가 없습니다."}
    return {"movie_id": movie_id, "average_sentiment": avg_score}

# 서버 실행 코드 (터미널 직접 실행용)
if __name__ == "__main__":
    import uvicorn

    # uvicorn FastAPI를 실행하는 ASGI 서버
    uvicorn.run(app, host="0.0.0.0", port=8000)
    # host="0.0.0.0": 모든 네트워크 인터페이스에서 접근 가능