# Streamlit 프론트엔드 - 영화 리뷰 앱

import streamlit as st
import requests
from datetime import datetime, date

# API 기본 URL
API_URL = "http://localhost:8000"

# 페이지 설정
st.set_page_config(
    page_title="🎬 Movie Review",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .movie-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 10px 0;
        transition: transform 0.3s;
        color: #333;
    }
    
    .movie-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 12px rgba(0, 0, 0, 0.2);
    }
    
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
    
    .review-card {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 10px 0;
        color: #333;
    }
    
    .review-card h4 {
        color: #667eea;
        margin-bottom: 8px;
    }
    
    .review-card p {
        color: #555;
        margin: 5px 0;
    }
    
    .main-title {
        color: white;
        text-align: center;
        font-size: 3em;
        font-weight: bold;
        margin-bottom: 30px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
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
    


# UI 아쉬워서 추가하는 코드
def render_sentiment_bar(score, show_label=True):
    """
    감성 점수를 시각적으로 표현하는 커스텀 bar
    
    Args:
        score: 0~1 사이의 감성 점수
        show_label: 점수와 레이블 표시 여부
    """
    position = score * 100
    
    if score >= 0.5:
        arrow = "↑"
        arrow_color = "#10b981"
        label_text = "긍정"
    else:
        arrow = "↓"
        arrow_color = "#ef4444"
        label_text = "부정"
    
    label_html = ""
    if show_label:
        label_html = f"""
<div style="display: flex; justify-content: center; gap: 20px; margin-bottom: 15px;">
<div style="background: white; padding: 10px 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center;">
<div style="font-size: 2em; font-weight: bold; color: {arrow_color};">
{arrow} {score:.3f}
</div>
<div style="font-size: 1.2em; color: {arrow_color}; font-weight: bold;">
{label_text}
</div>
</div>
</div>
"""
    
    html = f"""
<div style="margin: 20px 0;">
{label_html}
<div style="display: flex; justify-content: space-between; padding: 0 10px; margin-bottom: 5px;">
<span style="font-size: 1.5em;">😫</span>
<span style="font-size: 1.5em;">🤔</span>
<span style="font-size: 1.5em;">🤗</span>
</div>
<div style="position: relative; height: 35px; background: linear-gradient(to right, #ef4444 0%, #fbbf24 50%, #10b981 100%); border-radius: 20px; box-shadow: 0 3px 6px rgba(0,0,0,0.15);">
<div style="position: absolute; left: {position}%; top: 50%; transform: translate(-50%, -50%);">
<span style="font-size: 1.8em; filter: drop-shadow(0 1px 2px rgba(0,0,0,0.4));">🚩</span>
</div>
</div>
</div>
</div>
"""
    
    st.markdown(html, unsafe_allow_html=True)

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


def add_movie(title, release_date, director, genres, poster_url):
    """새로운 영화 추가"""
    movie_data = {
        "title": title,
        "release_date": release_date,
        "director": director,
        "genre": ", ".join(genres),  # 리스트를 문자열로 변환
        "poster_url": poster_url
    }
    try:
        response = requests.post(f"{API_URL}/movies", json=movie_data)
        response.raise_for_status()
        return True
    except Exception as e:
        st.error(f"영화 추가에 실패했습니다: {e}")
        return False


def update_movie(movie_id, title, release_date, director, genres, poster_url):
    """영화 정보 수정"""
    movie_data = {
        "id": movie_id,
        "title": title,
        "release_date": release_date,
        "director": director,
        "genre": ", ".join(genres),  # 리스트를 문자열로 변환
        "poster_url": poster_url
    }
    try:
        response = requests.put(f"{API_URL}/movies/{movie_id}", json=movie_data)
        response.raise_for_status()
        return True
    except Exception as e:
        st.error(f"영화 수정에 실패했습니다: {e}")
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
        cols = st.columns(3)
        
        for idx, movie in enumerate(movies):
            with cols[idx % 3]:
                st.markdown(f"""
                    <div class="movie-card">
                        <h3>🎬 {movie['title']}</h3>
                        <p><strong>감독:</strong> {movie['director']}</p>
                        <p><strong>장르:</strong> {movie['genre']}</p>
                        <p><strong>개봉일:</strong> {movie['release_date']}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                if movie['poster_url']:
                    st.image(movie['poster_url'], use_container_width=True)
                
                sentiment_data = get_average_sentiment(movie['id'])
                if sentiment_data and sentiment_data.get('average_sentiment') is not None:
                    avg_score = sentiment_data['average_sentiment']
                    render_sentiment_bar(avg_score, show_label=True)


def show_movie_add():
    """영화 등록 페이지"""
    st.header("🎬 새 영화 등록")
    
    genre_options = [
        "액션", "SF", "드라마", "코미디", "로맨스", 
        "스릴러", "호러", "애니메이션", "다큐멘터리", "판타지"
    ]
    
    with st.form("add_movie_form"):
        title = st.text_input("영화 제목 *", placeholder="예: 인터스텔라")
        
        col1, col2 = st.columns(2)
        with col1:
            director = st.text_input("감독 *", placeholder="예: 크리스토퍼 놀란")
            # 다중선택으로 변경
            genres = st.multiselect("장르 * (여러 개 선택 가능)", options=genre_options)
        
        with col2:
            # 1980년부터 선택 가능하도록
            release_date = st.date_input(
                "개봉일 *",
                min_value=date(1980, 1, 1),
                max_value=date.today()
            )
            poster_url = st.text_input("포스터 URL", placeholder="https://...")
        
        submitted = st.form_submit_button("✅ 영화 등록", use_container_width=True)
        
        if submitted:
            if not all([title, director, genres, release_date]):
                st.error("필수 항목을 모두 입력해주세요!")
            else:
                release_str = release_date.strftime("%Y-%m-%d")
                
                if add_movie(title, release_str, director, genres, poster_url or ""):
                    st.success(f"✅ '{title}' 영화가 등록되었습니다!")
                    # 풍선 제거
                    import time
                    time.sleep(2)
                    st.session_state.current_page = "홈"
                    st.rerun()


def show_movie_update():
    """영화 수정 페이지"""
    st.header("✏️ 영화 정보 수정")
    
    movies = get_movies()
    
    if not movies:
        st.warning("수정할 영화가 없습니다.")
    else:
        # 영화 선택
        movie_options = {f"{m['title']} ({m['director']})": m for m in movies}
        selected_movie_key = st.selectbox("수정할 영화 선택", options=list(movie_options.keys()))
        
        if selected_movie_key:
            selected_movie = movie_options[selected_movie_key]
            
            genre_options = [
                "액션", "SF", "드라마", "코미디", "로맨스", 
                "스릴러", "호러", "애니메이션", "다큐멘터리", "판타지"
            ]
            
            # 기존 장르를 리스트로 변환 (쉼표로 구분된 문자열)
            current_genres = [g.strip() for g in selected_movie['genre'].split(',')]
            
            with st.form("update_movie_form"):
                title = st.text_input("영화 제목 *", value=selected_movie['title'])
                
                col1, col2 = st.columns(2)
                with col1:
                    director = st.text_input("감독 *", value=selected_movie['director'])
                    genres = st.multiselect(
                        "장르 * (여러 개 선택 가능)", 
                        options=genre_options,
                        default=current_genres
                    )
                
                with col2:
                    # 기존 날짜를 datetime 객체로 변환
                    current_date = datetime.strptime(selected_movie['release_date'], "%Y-%m-%d").date()
                    release_date = st.date_input(
                        "개봉일 *",
                        value=current_date,
                        min_value=date(1980, 1, 1),
                        max_value=date.today()
                    )
                    poster_url = st.text_input("포스터 URL", value=selected_movie['poster_url'])
                
                submitted = st.form_submit_button("✅ 수정 완료", use_container_width=True)
                
                if submitted:
                    if not all([title, director, genres, release_date]):
                        st.error("필수 항목을 모두 입력해주세요!")
                    else:
                        release_str = release_date.strftime("%Y-%m-%d")
                        
                        if update_movie(selected_movie['id'], title, release_str, director, genres, poster_url):
                            st.success(f"✅ '{title}' 영화 정보가 수정되었습니다!")
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
        
        movie_options = {f"{m['title']} ({m['director']})": m for m in movies}
        selected_movie_key = st.selectbox("삭제할 영화 선택", options=list(movie_options.keys()))
        
        if selected_movie_key:
            selected_movie = movie_options[selected_movie_key]
            
            st.markdown(f"""
                <div class="movie-card">
                    <h3>🎬 {selected_movie['title']}</h3>
                    <p><strong>감독:</strong> {selected_movie['director']}</p>
                    <p><strong>장르:</strong> {selected_movie['genre']}</p>
                    <p><strong>개봉일:</strong> {selected_movie['release_date']}</p>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"🗑️ '{selected_movie['title']}' 삭제하기", type="primary", use_container_width=True):
                if delete_movie(selected_movie['id']):
                    st.success(f"✅ '{selected_movie['title']}' 영화가 삭제되었습니다!")
                    st.session_state.current_page = "홈"
                    st.rerun()


def show_review_write():
    """리뷰 작성 페이지"""
    st.header("✍️ 리뷰 작성하기")
    
    movies = get_movies()
    
    if not movies:
        st.warning("등록된 영화가 없습니다. 먼저 영화를 추가해주세요!")
    else:
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
                        review = add_review(movie_id, author, content)
                        
                        if review:
                            st.success("✅ 리뷰가 등록되었습니다!")
                            
                            score = review.get('sentiment_score', 0.5)
                            
                            st.subheader("🎯 감성 분석 결과")
                            render_sentiment_bar(score, show_label=True)
                            
                            # 풍선 제거
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
        movie_options = {f"{m['title']} ({m['director']})": m['id'] for m in movies}
        selected_movie = st.selectbox("영화 선택", options=list(movie_options.keys()))
        
        if selected_movie:
            movie_id = movie_options[selected_movie]
            reviews = get_reviews_by_movie(movie_id)
            
            if not reviews:
                st.info("아직 작성된 리뷰가 없습니다.")
            else:
                st.subheader(f"💬 총 {len(reviews)}개의 리뷰")
                
                sentiment_data = get_average_sentiment(movie_id)
                if sentiment_data and sentiment_data.get('average_sentiment') is not None:
                    avg_score = sentiment_data['average_sentiment']
                    
                    render_sentiment_bar(avg_score, show_label=True)
                
                st.divider()
                
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
                    
                    render_sentiment_bar(score, show_label=False)


# 메인 앱

def main():
    st.markdown('<h1 class="main-title">🎬 영화 리뷰 ✨</h1>', unsafe_allow_html=True)
    
    st.sidebar.title("📋 메뉴")
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "홈"
    
    if st.sidebar.button("🏠 홈", use_container_width=True):
        st.session_state.current_page = "홈"
    
    with st.sidebar.expander("🎬 영화", expanded=True):
        if st.button("➕ 영화 등록", use_container_width=True):
            st.session_state.current_page = "영화 등록"
        if st.button("✏️ 영화 수정", use_container_width=True):
            st.session_state.current_page = "영화 수정"
        if st.button("🗑️ 영화 삭제", use_container_width=True):
            st.session_state.current_page = "영화 삭제"
    
    with st.sidebar.expander("📝 리뷰", expanded=True):
        if st.button("✍️ 리뷰 작성", use_container_width=True):
            st.session_state.current_page = "리뷰 작성"
        if st.button("📊 리뷰 보기", use_container_width=True):
            st.session_state.current_page = "리뷰 보기"
    
    if st.session_state.current_page == "홈":
        show_home()
    elif st.session_state.current_page == "영화 등록":
        show_movie_add()
    elif st.session_state.current_page == "영화 수정":
        show_movie_update()
    elif st.session_state.current_page == "영화 삭제":
        show_movie_delete()
    elif st.session_state.current_page == "리뷰 작성":
        show_review_write()
    elif st.session_state.current_page == "리뷰 보기":
        show_review_list()


if __name__ == "__main__":
    main()