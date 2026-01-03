# =========================
# evaluate_sentiment.py
# =========================

from transformers import pipeline
from datasets import load_dataset
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# --- 1. Load model ---
print("Loading model...")
analyzer = pipeline(
    "sentiment-analysis",
    model="wonrax/phobert-base-vietnamese-sentiment",
    batch_size=16,
    truncation=True
)

# --- 2. Load dataset ---
print("Loading UIT-VSFC...")
dataset = load_dataset("ura-hcmut/UIT-VSFC")
test_data = dataset["test"]

texts = [item["text"][:256] for item in test_data]

# --- 3. MAP LABEL DATASET → LABEL MODEL ---
label_map = {
    "negative": "NEG",
    "neutral": "NEU",
    "positive": "POS"
}

y_true = [label_map[item["label"]] for item in test_data]

# --- 4. Inference ---
print("Running batch inference...")
results = analyzer(texts)
y_pred = [r["label"] for r in results]

# --- 5. Metrics ---
labels = ["NEG", "NEU", "POS"]

print("\n================ RESULTS ================\n")

print("Accuracy:")
print(accuracy_score(y_true, y_pred))

print("\nClassification Report:")
print(classification_report(
    y_true,
    y_pred,
    labels=labels,
    target_names=labels,
    digits=4,
    zero_division=0
))

print("\nConfusion Matrix:")
print(confusion_matrix(y_true, y_pred, labels=labels))


'''
🧠 Ý NGHĨA TỪNG METRIC (NGẮN – ĐÚNG)

Accuracy
→ Tổng thể đoán đúng bao nhiêu %

Precision (theo class)
→ Model nói “NEG” thì đúng bao nhiêu %

Recall (theo class)
→ Các câu NEG thật, model bắt được bao nhiêu %

F1-score
→ Cân bằng Precision & Recall

Macro avg
→ Trung bình các class (không quan tâm class to/nhỏ)

Weighted avg
→ Trung bình có tính số lượng mỗi class (dùng nhiều nhất)

Confusion Matrix
→ Nhìn được model hay nhầm NEG ↔ NEU, NEU ↔ POS
'''



'''
PS D:\djangoProject>  python evaluate_sentiment.py
Loading model...
Device set to use cpu
Loading UIT-VSFC...
Running batch inference...

================ RESULTS ================

Accuracy:
0.7040429564118762

Classification Report:
              precision    recall  f1-score   support

         NEG     0.8807    0.5451    0.6734      1409
         NEU     0.1388    0.5569    0.2222       167
         POS     0.8424    0.8604    0.8513      1590

    accuracy                         0.7040      3166
   macro avg     0.6206    0.6541    0.5823      3166
weighted avg     0.8223    0.7040    0.7389      3166


Confusion Matrix:
[[ 768  442  199]
 [  17   93   57]
 [  87  135 1368]]

'''