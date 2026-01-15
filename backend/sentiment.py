# 한국어 리뷰 감성 분석 모듈
# nlp04/korean_sentiment_analysis_kcelectra 모델 사용

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# 전역 변수로 모델과 토크나이저를 저장
# 매번 로드하면 느리니까 한 번만 로드해서 재사용

_model = None
_tokenizer = None


def load_model():
    """
    감성 분석 모델과 토크나이저를 메모리에 로드
    처음 한 번 실행, 이후로는 캐싱된 모델 사용

    Returns:
        model: 감성 분석용 파인튜닝된 모델
        tokenizer: 텍스트를 모델 입력으로 변환
    """

    global _model, _tokenizer

    # 로드되어 있으면 재로드하지 않음
    if _model is not None and _tokenizer is not None:
        return _model, _tokenizer
    
    print("감성 분석 모델을 로딩 중입니다! ⚙")

    # 허깅페이스에서 모델 이름 지정
    model_name =