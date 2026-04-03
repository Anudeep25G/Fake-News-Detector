import pandas as pd
import numpy as np
import re
import pickle
import os
import sklearn

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

os.makedirs("model", exist_ok=True)

print(f"sklearn version: {sklearn.__version__}")  # verify this matches Streamlit env

# -----------------------------------------------------------------------
# 1. LOAD DATA
# -----------------------------------------------------------------------
fake = pd.read_csv("data/Fake.csv")
true = pd.read_csv("data/True.csv")

print(f"Fake articles : {len(fake)}")
print(f"True articles : {len(true)}")

# -----------------------------------------------------------------------
# 2. LABEL DATA
# -----------------------------------------------------------------------
fake["label"] = 0
true["label"] = 1

# -----------------------------------------------------------------------
# 3. REMOVE REUTERS SOURCE LEAK (FIX 1 — critical)
#    True.csv articles start with "CITY, STATE (Reuters) —"
#    The model was learning "Reuters" = real, not actual content.
# -----------------------------------------------------------------------
def remove_source_tag(text):
    text = re.sub(r'^[A-Z ,]+\(Reuters\)\s*-\s*', '', str(text))
    return text

true["text"] = true["text"].apply(remove_source_tag)

# -----------------------------------------------------------------------
# 4. BALANCE DATASET
# -----------------------------------------------------------------------
min_len = min(len(fake), len(true))
fake = fake.sample(min_len, random_state=42)
true = true.sample(min_len, random_state=42)

# -----------------------------------------------------------------------
# 5. COMBINE & SHUFFLE
# -----------------------------------------------------------------------
data = pd.concat([fake, true]).sample(frac=1, random_state=42).reset_index(drop=True)

# -----------------------------------------------------------------------
# 6. CLEAN TEXT
# -----------------------------------------------------------------------
def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'http\S+|www\S+', '', text)
    text = re.sub(r'\d+', '', text)
    text = re.sub(r'[^a-z\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

data["title"] = data["title"].apply(clean_text)
data["text"]  = data["text"].apply(clean_text)

# -----------------------------------------------------------------------
# 7. COMBINE TITLE + TEXT (title repeated 2x for higher TF-IDF weight)
# -----------------------------------------------------------------------
data["content"] = data["title"] + " " + data["title"] + " " + data["text"]

X = data["content"]
y = data["label"]

# -----------------------------------------------------------------------
# 8. TF-IDF VECTORIZATION
# -----------------------------------------------------------------------
vectorizer = TfidfVectorizer(
    max_features=50000,
    stop_words="english",
    ngram_range=(1, 2),
    min_df=3,
    max_df=0.85,
    sublinear_tf=True,
)
X_vec = vectorizer.fit_transform(X)

# -----------------------------------------------------------------------
# 9. TRAIN / TEST SPLIT
# -----------------------------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X_vec, y, test_size=0.2, random_state=42, stratify=y
)

# -----------------------------------------------------------------------
# 10. MODEL — Logistic Regression
#     solver='lbfgs' is the new default in sklearn 1.8+ and works well
#     for binary classification. No multi_class needed (binary auto).
# -----------------------------------------------------------------------
print("\nTraining Logistic Regression ...")
model = LogisticRegression(
    C=2,
    max_iter=1000,
    solver="lbfgs",       # changed from saga — compatible with sklearn 1.8+
    random_state=42,
)
model.fit(X_train, y_train)

# -----------------------------------------------------------------------
# 11. EVALUATION
# -----------------------------------------------------------------------
y_pred  = model.predict(X_test)
y_proba = model.predict_proba(X_test)[:, 1]

acc = accuracy_score(y_test, y_pred)
print(f"\n{'='*50}")
print(f"  Accuracy : {acc * 100:.2f}%")
print(f"{'='*50}")
print("\nClassification Report:\n")
print(classification_report(y_test, y_pred, target_names=["FAKE", "REAL"]))

cm = confusion_matrix(y_test, y_pred)
tn, fp, fn, tp = cm.ravel()
print(f"Confusion Matrix:")
print(f"  True Negatives  (FAKE→FAKE) : {tn}")
print(f"  False Positives (FAKE→REAL) : {fp}  <- fake predicted as real")
print(f"  False Negatives (REAL→FAKE) : {fn}")
print(f"  True Positives  (REAL→REAL) : {tp}")

# -----------------------------------------------------------------------
# 12. CROSS-VALIDATION
# -----------------------------------------------------------------------
print("\nRunning 5-fold cross-validation ...")
cv_scores = cross_val_score(model, X_vec, y, cv=5, scoring="f1")
print(f"  CV F1 scores : {cv_scores.round(4)}")
print(f"  Mean F1      : {cv_scores.mean():.4f} +/- {cv_scores.std():.4f}")

# -----------------------------------------------------------------------
# 13. SAVE MODEL & VECTORIZER
# -----------------------------------------------------------------------
pickle.dump(model,      open("model/model.pkl",     "wb"))
pickle.dump(vectorizer, open("model/vectorizer.pkl", "wb"))

print("\nModel and Vectorizer saved to model/")
