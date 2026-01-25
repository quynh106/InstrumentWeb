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




def analyze_sentiment(text: str) -> str:
    if not text or not text.strip():  #tiền xử lý: Tránh AI phân tích chuỗi trống, tránh lỗi.
        return "neutral"

    analyzer = get_sentiment_analyzer()
    result = analyzer(text[:256])[0]     #Cắt độ dài text để tối ưu hiệu năng

    label = result["label"].upper()

    if label == "POS":
        return "positive"
    elif label == "NEG":
        return "negative"
    return "neutral"

