from transformers import pipeline

_sentiment_analyzer = None  # cache model

def get_sentiment_analyzer():
    global _sentiment_analyzer
    if _sentiment_analyzer is None:
        _sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model="wonrax/phobert-base-vietnamese-sentiment"  #Sử dụng mô hình PhoBERT pretrained cho tiếng Việt
        )
    return _sentiment_analyzer


def is_negative_comment(text: str) -> bool:
    if not text or not text.strip():    #tiền xử lý: Tránh AI phân tích chuỗi trống, tránh lỗi.
        return False

    analyzer = get_sentiment_analyzer()
    result = analyzer(text[:256])[0]    #Cắt độ dài text để tối ưu hiệu năng

    label = result["label"].upper()
    score = result["score"]

 # Chỉ coi là tiêu cực khi NEG + độ tin cậy của dự đoán cao
    return label == "NEG" and score > 0.8




