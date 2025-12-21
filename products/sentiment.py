from transformers import pipeline

# Load model sentiment tiếng Việt
sentiment_analyzer = pipeline(
    "sentiment-analysis",
    model="wonrax/phobert-base-vietnamese-sentiment"   #Sử dụng mô hình PhoBERT pretrained cho tiếng Việt
)

def is_negative_comment(text: str) -> bool:
    if not text or not text.strip():  #tiền xử lý: Tránh AI phân tích chuỗi trống, tránh lỗi.
        return False

    result = sentiment_analyzer(text[:256])[0]   #Cắt độ dài text để tối ưu hiệu năng
    label = result["label"].upper()
    score = result["score"]

    # Chỉ coi là tiêu cực khi NEG + độ tin cậy cao
    return label == "NEG" and score > 0.8
