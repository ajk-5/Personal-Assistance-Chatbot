from __future__ import annotations
from typing import List, Optional, Tuple

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import Pipeline
    SKLEARN_OK = True
except Exception:  # pragma: no cover
    SKLEARN_OK = False

from django.db.utils import OperationalError, ProgrammingError
from .models import TrainingPhrase

class IntentRouter:
    """TF‑IDF + Logistic Regression classifier (optional).

    Falls back to None if scikit‑learn is not available or insufficient data.
    """

    def __init__(self) -> None:
        self.enabled = SKLEARN_OK
        self.pipeline: Optional[Pipeline] = None
        self.labels: List[str] = []
        self.threshold: float = 0.55

    def collect_training(self) -> Tuple[List[str], List[str]]:
        X: List[str] = []
        y: List[str] = []
        # Built‑ins (seed data)
        seed = {
            "tasks": ["add task", "list tasks", "complete task"],
            "notes": ["note", "list notes", "search notes"],
            "reminders": ["remind me", "list reminders", "cancel reminder"],
            "events": ["add event", "list events", "delete event"],
            "time": ["what time is it", "date", "timezone"],
            "smalltalk": ["hello", "thanks", "bye"],
            "profile": ["about me", "who am i", "tell me about myself"],
            "projects": ["my projects", "what projects am i doing", "show projects"],
            "help": ["help", "how to use", "commands", "what can you do"],
        }
        for lbl, phrases in seed.items():
            for p in phrases:
                X.append(p); y.append(lbl)
        # User-taught phrases from DB (guarded: during first migrations table may not exist)
        try:
            for tp in TrainingPhrase.objects.all():
                X.append(tp.text); y.append(tp.label)
        except (OperationalError, ProgrammingError):
            # Database not ready (e.g., before migrations). Proceed with seeds only.
            pass
        return X, y

    def train(self) -> str:
        if not self.enabled:
            self.pipeline = None
            return "ML disabled (install scikit‑learn)."
        X, y = self.collect_training()
        if len(set(y)) < 2:
            self.pipeline = None
            return "Not enough distinct labels. Use admin or a form to add TrainingPhrase."
        self.pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), lowercase=True)),
            ("clf", LogisticRegression(max_iter=1000)),
        ])
        self.pipeline.fit(X, y)
        self.labels = sorted(set(y))
        return f"Trained on {len(X)} phrases across {len(self.labels)} labels."

    def predict(self, text: str) -> Tuple[Optional[str], float]:
        if not (self.enabled and self.pipeline):
            return None, 0.0
        proba = self.pipeline.predict_proba([text])[0]
        idx = int(proba.argmax())
        label = self.pipeline.classes_[idx]
        conf = float(proba[idx])
        return label, conf
