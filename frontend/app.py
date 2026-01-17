# Streamlit 프론트엔드 - 영화 리뷰 앱

import streamlit as st
import requests
from datetime import datetime

# API 기본 URL
API_URL = "http://localhost:8000"

# 페이지 설정
st.set_page_config(
    page_title="🎬 Movie Review",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS로 디자인 개선
st.markdown("""
    <style>
    /* 전체 앱 배경 */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* 카드 스타일 */
    .movie-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 10px 0;
        transition: transform 0.3s;
        color: #333;  /* ✅ 추가! 기본 텍스트 색상 */
    }
    
    .movie-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 12px rgba(0, 0, 0, 0.2);
    }
    
    /* ✅ 추가! 카드 내부 요소 색상 지정 */
    .movie-card h3 {
        color: #667eea;
        margin-bottom: 10px;
        font-size: 1.3em;
    }
    
    .movie-card p {
        color: #555;
        margin: 5px 0;
        line-height: 1.6;
    }
    
    .movie-card strong {
        color: #333;
    }
    
    /* 리뷰 카드 */
    .review-card {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 10px 0;
        color: #333;  /* ✅ 추가! */
    }
    
    .review-card h4 {
        color: #667eea;  /* ✅ 추가! */
        margin-bottom: 8px;
    }
    
    .review-card p {
        color: #555;  /* ✅ 추가! */
        margin: 5px 0;
    }
    
    /* 제목 스타일 */
    .main-title {
        color: white;
        text-align: center;
        font-size: 3em;
        font-weight: bold;
        margin-bottom: 30px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    /* 사이드바 버튼 스타일 */
    .stButton button {
        width: 100%;
        background: white;
        color: #667eea;
        border: none;
        border-radius: 10px;
        padding: 10px;
        font-weight: bold;
        transition: all 0.3s;
    }
    
    .stButton button:hover {
        background: #667eea;
        color: white;
        transform: translateX(5px);
    }
    </style>
""", unsafe_allow_html=True)


# 유틸리티 함수들

def get_sentiment_emoji(score):
    """감성 점수에 따라 이모지 반환"""
    if score >= 0.7:
        return "😊"
    elif score >= 0.4:
        return "😐"
    else:
        return "😞"


def get_sentiment_label(score):
    """감성 점수에 따라 레이블 반환"""
    if score >= 0.7:
        return "긍정"
    elif score >= 0.4:
        return "중립"
    else:
        return "부정"


# API 호출 함수들

def get_movies():
    """모든 영화 목록 조회"""
    try:
        response = requests.get(f"{API_URL}/movies")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"영화 목록을 불러오는데 실패했습니다: {e}")
        return []


def add_movie(title, release_date, director, genre, poster_url):
    """새로운 영화 추가"""
    movie_data = {
        "title": title,
        "release_date": release_date,
        "director": director,
        "genre": genre,
        "poster_url": poster_url
    }
    try:
        response = requests.post(f"{API_URL}/movies", json=movie_data)
        response.raise_for_status()
        return True
    except Exception as e:
        st.error(f"영화 추가에 실패했습니다: {e}")
        return False


def delete_movie(movie_id):
    """영화 삭제"""
    try:
        response = requests.delete(f"{API_URL}/movies/{movie_id}")
        response.raise_for_status()
        return True
    except Exception as e:
        st.error(f"영화 삭제에 실패했습니다: {e}")
        return False


def get_reviews_by_movie(movie_id):
    """특정 영화의 리뷰 조회"""
    try:
        response = requests.get(f"{API_URL}/movies/{movie_id}/reviews")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"리뷰를 불러오는데 실패했습니다: {e}")
        return []


def add_review(movie_id, author, content):
    """새로운 리뷰 추가"""
    review_data = {
        "movie_id": movie_id,
        "author": author,
        "content": content
    }
    try:
        response = requests.post(f"{API_URL}/reviews", json=review_data)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"리뷰 추가에 실패했습니다: {e}")
        return None


def get_average_sentiment(movie_id):
    """영화의 평균 감성 점수 조회"""
    try:
        response = requests.get(f"{API_URL}/movies/{movie_id}/sentiment")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return None


# 페이지 함수들

def show_home():
    """홈 페이지"""
    st.header("🎥 전체 영화 목록")
    
    movies = get_movies()
    
    if not movies:
        st.info("등록된 영화가 없습니다. 영화를 추가해보세요!")
    else:
        # 3열 그리드로 영화 카드 표시
        cols = st.columns(3)
        
        for idx, movie in enumerate(movies):
            with cols[idx % 3]:
                # 영화 카드
                st.markdown(f"""
                    <div class="movie-card">
                        <h3>🎬 {movie['title']}</h3>
                        <p><strong>감독:</strong> {movie['director']}</p>
                        <p><strong>장르:</strong> {movie['genre']}</p>
                        <p><strong>개봉일:</strong> {movie['release_date']}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                # 포스터 이미지
                if movie['poster_url']:
                    st.image(movie['poster_url'], use_container_width=True)
                
                # 평균 감성 점수 표시
                sentiment_data = get_average_sentiment(movie['id'])
                if sentiment_data and sentiment_data.get('average_sentiment') is not None:
                    avg_score = sentiment_data['average_sentiment']
                    st.metric(
                        label="평균 감성 점수",
                        value=f"{avg_score:.2f}",
                        delta=get_sentiment_label(avg_score)
                    )
                    st.progress(avg_score)


def show_movie_add():
    """영화 등록 페이지"""
    st.header("🎬 새 영화 등록")
    
    # 장르 옵션 (드롭다운용)
    genre_options = [
        "액션", "SF", "드라마", "코미디", "로맨스", 
        "스릴러", "호러", "애니메이션", "다큐멘터리", "판타지"
    ]
    
    with st.form("add_movie_form"):
        title = st.text_input("영화 제목 *", placeholder="예: 인터스텔라")
        
        col1, col2 = st.columns(2)
        with col1:
            director = st.text_input("감독 *", placeholder="예: 크리스토퍼 놀란")
            # 드롭다운으로 장르 선택
            genre = st.selectbox("장르 *", options=genre_options)
        
        with col2:
            release_date = st.date_input("개봉일 *")
            poster_url = st.text_input("포스터 URL", placeholder="https://...")
        
        submitted = st.form_submit_button("✅ 영화 등록", use_container_width=True)
        
        if submitted:
            if not all([title, director, genre, release_date]):
                st.error("필수 항목을 모두 입력해주세요!")
            else:
                # 날짜 형식 변환
                release_str = release_date.strftime("%Y-%m-%d")
                
                if add_movie(title, release_str, director, genre, poster_url or ""):
                    st.success(f"✅ '{title}' 영화가 등록되었습니다!")
                    st.balloons()
                    # ✅ 2초 후 홈으로 자동 이동
                    import time
                    time.sleep(2)
                    st.session_state.current_page = "홈"
                    st.rerun()


def show_movie_delete():
    """영화 삭제 페이지"""
    st.header("🗑️ 영화 삭제")
    
    movies = get_movies()
    
    if not movies:
        st.warning("삭제할 영화가 없습니다.")
    else:
        st.warning("⚠️ 영화를 삭제하면 관련된 모든 리뷰도 함께 삭제됩니다!")
        
        # 영화 선택
        movie_options = {f"{m['title']} ({m['director']})": m for m in movies}
        selected_movie_key = st.selectbox("삭제할 영화 선택", options=list(movie_options.keys()))
        
        if selected_movie_key:
            selected_movie = movie_options[selected_movie_key]
            
            # 선택한 영화 정보 표시
            st.markdown(f"""
                <div class="movie-card">
                    <h3>🎬 {selected_movie['title']}</h3>
                    <p><strong>감독:</strong> {selected_movie['director']}</p>
                    <p><strong>장르:</strong> {selected_movie['genre']}</p>
                    <p><strong>개봉일:</strong> {selected_movie['release_date']}</p>
                </div>
            """, unsafe_allow_html=True)
            
            # 삭제 확인 버튼
            if st.button(f"🗑️ '{selected_movie['title']}' 삭제하기", type="primary", use_container_width=True):
                if delete_movie(selected_movie['id']):
                    st.success(f"✅ '{selected_movie['title']}' 영화가 삭제되었습니다!")
                    # ✅ 홈으로 자동 이동
                    st.session_state.current_page = "홈"
                    st.rerun()


def show_review_write():
    """리뷰 작성 페이지"""
    st.header("✍️ 리뷰 작성하기")
    
    movies = get_movies()
    
    if not movies:
        st.warning("등록된 영화가 없습니다. 먼저 영화를 추가해주세요!")
    else:
        # 영화 선택
        movie_options = {f"{m['title']} ({m['director']})": m['id'] for m in movies}
        selected_movie = st.selectbox("영화 선택", options=list(movie_options.keys()))
        
        if selected_movie:
            movie_id = movie_options[selected_movie]
            
            with st.form("add_review_form"):
                author = st.text_input("작성자 이름 *", placeholder="예: 무무")
                content = st.text_area(
                    "리뷰 내용 *",
                    placeholder="영화에 대한 솔직한 감상을 남겨주세요...",
                    height=150
                )
                
                submitted = st.form_submit_button("✅ 리뷰 등록", use_container_width=True)
                
                if submitted:
                    if not all([author, content]):
                        st.error("모든 항목을 입력해주세요!")
                    else:
                        # 리뷰 추가
                        review = add_review(movie_id, author, content)
                        
                        if review:
                            st.success("✅ 리뷰가 등록되었습니다!")
                            
                            # 감성 분석 결과 표시
                            score = review.get('sentiment_score', 0.5)
                            
                            st.subheader("🎯 감성 분석 결과")
                            
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric(
                                    label="감성 점수",
                                    value=f"{score:.3f}"
                                )
                            
                            with col2:
                                st.metric(
                                    label="감성 분류",
                                    value=get_sentiment_label(score)
                                )
                            
                            with col3:
                                st.markdown(
                                    f"<h1 style='text-align: center;'>{get_sentiment_emoji(score)}</h1>",
                                    unsafe_allow_html=True
                                )
                            
                            # 감성 점수 바
                            st.progress(score)
                            
                            st.balloons()
                            
                            # ✅ 3초 후 리뷰 보기로 자동 이동
                            import time
                            time.sleep(3)
                            st.session_state.current_page = "리뷰 보기"
                            st.rerun()


def show_review_list():
    """리뷰 목록 페이지"""
    st.header("📊 리뷰 목록")
    
    movies = get_movies()
    
    if not movies:
        st.warning("등록된 영화가 없습니다.")
    else:
        # 영화 선택
        movie_options = {f"{m['title']} ({m['director']})": m['id'] for m in movies}
        selected_movie = st.selectbox("영화 선택", options=list(movie_options.keys()))
        
        if selected_movie:
            movie_id = movie_options[selected_movie]
            reviews = get_reviews_by_movie(movie_id)
            
            if not reviews:
                st.info("아직 작성된 리뷰가 없습니다.")
            else:
                st.subheader(f"💬 총 {len(reviews)}개의 리뷰")
                
                # 평균 감성 점수
                sentiment_data = get_average_sentiment(movie_id)
                if sentiment_data and sentiment_data.get('average_sentiment') is not None:
                    avg_score = sentiment_data['average_sentiment']
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("평균 감성 점수", f"{avg_score:.3f}")
                    with col2:
                        st.metric("전체 평가", get_sentiment_label(avg_score))
                    with col3:
                        st.markdown(
                            f"<h1 style='text-align: center;'>{get_sentiment_emoji(avg_score)}</h1>",
                            unsafe_allow_html=True
                        )
                    
                    st.progress(avg_score)
                
                st.divider()
                
                # 리뷰 목록
                for review in reviews:
                    score = review.get('sentiment_score', 0.5)
                    
                    st.markdown(f"""
                        <div class="review-card">
                            <h4>{get_sentiment_emoji(score)} {review['author']}</h4>
                            <p>{review['content']}</p>
                            <p><small>📅 {review['created_at']} | 
                            감성 점수: <strong>{score:.3f}</strong> ({get_sentiment_label(score)})</small></p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # 감성 점수 바
                    st.progress(score)


# 메인 앱

def main():
    # 메인 타이틀
    st.markdown('<h1 class="main-title">🎬 영화 리뷰 ✨</h1>', unsafe_allow_html=True)
    
    # 사이드바 메뉴
    st.sidebar.title("📋 메뉴")
    
    # 세션 상태 초기화
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "홈"
    
    # 버튼 형식 메뉴
    if st.sidebar.button("🏠 홈", use_container_width=True):
        st.session_state.current_page = "홈"
    
    # 영화 메뉴 (확장 가능)
    with st.sidebar.expander("🎬 영화", expanded=True):
        if st.button("➕ 영화 등록", use_container_width=True):
            st.session_state.current_page = "영화 등록"
        if st.button("🗑️ 영화 삭제", use_container_width=True):
            st.session_state.current_page = "영화 삭제"
    
    # 리뷰 메뉴 (확장 가능)
    with st.sidebar.expander("📝 리뷰", expanded=True):
        if st.button("✍️ 리뷰 작성", use_container_width=True):
            st.session_state.current_page = "리뷰 작성"
        if st.button("📊 리뷰 보기", use_container_width=True):
            st.session_state.current_page = "리뷰 보기"
    
    # 페이지 라우팅
    if st.session_state.current_page == "홈":
        show_home()
    elif st.session_state.current_page == "영화 등록":
        show_movie_add()
    elif st.session_state.current_page == "영화 삭제":
        show_movie_delete()
    elif st.session_state.current_page == "리뷰 작성":
        show_review_write()
    elif st.session_state.current_page == "리뷰 보기":
        show_review_list()


if __name__ == "__main__":
    main()