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
    model_name = "nlp04/korean_sentiment_analysis_kcelectra"

    # 토크나이저 로드
    _tokenizer = AutoTokenizer.from_pretrained(model_name)

    # 모델 로드
    # AutoModelForSequenceClassification: 텍스트 분류용 모델
    _model = AutoModelForSequenceClassification.from_pretrained(model_name)

    # 모델을 평가 모드로 설정
    # eval(): 학습 모드가 아닌 추론(예측) 모드로 전환
    # 드롭아웃, 배치 정규화 등이 비활성화됨
    _model.eval()

    print("모델 로딩 완료")

    return _model, _tokenizer

# 클래스 label이 2개가 아니라 11개인 걸 깨닫고나서 수정 들어감
def analyze_sentiment(text: str) -> float:
    """
    텍스트에서 감성을 분석하여 0~1 사이의 점수를 반환
    """

    # 빈 텍스트 처리
    if not text or not text.strip():
        return 0.5

    _model, _tokenizer = load_model()
    
    # 텍스트를 모델이 이해할 수 있는 형태로 변환시킬 것
    inputs = _tokenizer(
        text,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=512
    )

    # 그래디언트 계산 비활성화 (추론 시에는 필요 없음, 메모리 절약)
    with torch.no_grad():
        # 모델에 입력 전달하여 예측 수행
        # outputs.logits: 각 클래스(긍정/부정)에 대한 raw 점수
        outputs = _model(**inputs)

    # logits를 확률로 변환
    # softmax: 각 클래스의 점수를 0~1 사이 확률로 변환 (합이 1이 되는 거)
    # dim=1: 마지막 차원(클래스 차원)에 대해 softmax 적용
    probabilities = torch.nn.functional.softmax(outputs.logits, dim=1)

    # -----디버깅: 클래스 레이블 확인-----
    # print(f"\n모델 클래스 레이블: {_model.config.id2label}")
    # print(f"확률 분포: {probabilities[0].tolist()}")
    # ----------------------------------

    # 감정 인덱스 매핑 - 디버깅 후 추가

    positive_indices = [0, 1, 2, 3, 4]
    # 0(기쁨), 1(고마운), 2(설레는), 3(사랑하는), 4(즐거운)
    negative_indices = [7, 8, 9, 10]
    # 7(슬픔), 8(힘듦), 9(짜증남), 10(걱정스러운)
    neutral_indices = [5, 6]
    # 5(일상적인), 6(생각이 많은)

    # 감정 그룹의 확률 합계를 계산하는 부분 한줄코딩
    positive_score = sum(probabilities[0][i].item() for i in positive_indices)
    negative_score = sum(probabilities[0][i].item() for i in negative_indices)
    neutral_score = sum(probabilities[0][i].item() for i in neutral_indices)

    # 긍정 +중립*0.5 비율로 최종 점수 계산
    # 중립은 절반만 긍정으로 계산
    total = positive_score + negative_score + neutral_score

    if total == 0:
        return 0.5
    
    # 긍정 비율 계산 (중립은 0.5 가중치)
    sentiment_score = (positive_score + neutral_score*0.5) / total

    return sentiment_score


def analyze_sentiment_batch(texts: list) -> list:
    """
    여러 텍스트를 한 번에 분석 (배치 처리)
    """
    if not texts:
        return []
    
    processed_texts = []
    empty_indices = []
    
    for i, text in enumerate(texts):
        if text and text.strip():
            processed_texts.append(text)
        else:
            empty_indices.append(i)
    
    if not processed_texts:
        return [0.5] * len(texts)
    
    _model, _tokenizer = load_model()
    
    inputs = _tokenizer(
        processed_texts,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=512
    )
    
    with torch.no_grad():
        outputs = _model(**inputs)
    
    probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
    
    # 감정 인덱스 매핑
    positive_indices = [0, 1, 2, 3, 4]
    negative_indices = [7, 8, 9, 10]
    neutral_indices = [5, 6]
    
    scores = []
    for i in range(len(processed_texts)):
        positive_score = sum(probabilities[i][idx].item() for idx in positive_indices)
        negative_score = sum(probabilities[i][idx].item() for idx in negative_indices)
        neutral_score = sum(probabilities[i][idx].item() for idx in neutral_indices)
        
        total = positive_score + negative_score + neutral_score
        
        if total == 0:
            scores.append(0.5)
        else:
            # 괄호 추가!
            sentiment_score = (positive_score + neutral_score * 0.5) / total
            scores.append(sentiment_score)
    
    # 빈 텍스트 위치에 중립 점수 삽입
    for idx in empty_indices:
        scores.insert(idx, 0.5)
    
    return scores
    


# 테스트 코드 (이 파일을 직접 실행했을 때만 작동)
if __name__ == "__main__":
    # 테스트용 리뷰 예시
    test_reviews = [
        "정말 감동적인 영화였어요! 최고!",
        "시간 낭비였습니다. 별로예요.",
        "그냥 평범한 영화네요",
        "연기가 너무 좋았고 스토리도 탄탄했어요",
        "돈 아까워요 ㅠㅠ"
    ]
    
    print("\n---감성 분석 테스트---\n")
    
    for review in test_reviews:
        score = analyze_sentiment(review)
        print(f"리뷰: {review}")
        print(f"감성 점수: {score:.3f}")
        
        # 점수에 따른 레이블 출력
        if score > 0.7:
            sentiment = "😊 긍정"
        elif score < 0.3:
            sentiment = "😞 부정"
        else:
            sentiment = "😐 중립"
        
        print(f"판단: {sentiment}\n")