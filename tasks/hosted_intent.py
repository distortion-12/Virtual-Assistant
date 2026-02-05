"""
Hosted Intent Router
Uses a free hosted model (Hugging Face Inference API) to classify user intent
and normalize commands for task planning.
"""

import os
import re
from typing import Optional, Dict, Any

import requests


class HostedIntentRouter:
    """Optional hosted intent classifier for better task understanding"""

    LABELS = [
        "open_app",
        "search_web",
        "get_time",
        "get_date",
        "get_weather",
        "system_info",
        "file_operation",
        "knowledge_query",
    ]

    def __init__(
        self,
        model: str,
        api_token: str,
        min_score: float = 0.55,
        timeout: int = 8,
    ):
        self.model = model
        self.api_token = api_token
        self.min_score = min_score
        self.timeout = timeout
        self.api_url = f"https://api-inference.huggingface.co/models/{model}"
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "User-Agent": "Zenith/1.0 (https://example.com; contact: local)",
        }

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> Optional["HostedIntentRouter"]:
        enabled = config.get("ai_intent_enabled", False)
        if not enabled:
            return None

        model = config.get("hf_model", "facebook/bart-large-mnli")
        min_score = float(config.get("hf_min_score", 0.55))
        api_token = config.get("hf_api_token") or os.getenv("HF_API_TOKEN")
        if not api_token:
            return None

        return cls(model=model, api_token=api_token, min_score=min_score)

    def classify(self, text: str) -> Optional[Dict[str, Any]]:
        payload = {
            "inputs": text,
            "parameters": {"candidate_labels": self.LABELS},
        }

        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=self.timeout,
            )
            if response.status_code != 200:
                return None

            data = response.json()
            labels = data.get("labels")
            scores = data.get("scores")
            if not labels or not scores:
                return None

            return {"label": labels[0], "score": scores[0]}
        except Exception:
            return None

    def normalize_command(self, text: str) -> Optional[str]:
        result = self.classify(text)
        if not result or result["score"] < self.min_score:
            return None

        label = result["label"]
        if label == "get_time":
            return "time"
        if label == "get_date":
            return "date"
        if label == "get_weather":
            return "weather"
        if label == "system_info":
            return "system info"
        if label == "open_app":
            app = self._extract_app_name(text)
            return f"open {app}" if app else None
        if label == "search_web":
            query = self._extract_query(text, ["search", "find", "look up"])
            return f"search {query}" if query else "search " + text
        if label == "file_operation":
            return text
        if label == "knowledge_query":
            return text

        return None

    def _extract_app_name(self, text: str) -> str:
        text = text.lower().strip()
        # Remove common phrases
        patterns = [
            r"^(please\s+)?(open|launch|start)\s+",
            r"^(can|could|would|will)\s+you\s+(open|launch|start)\s+",
            r"^(i\s+want\s+to\s+)(open|launch|start)\s+",
        ]
        for pattern in patterns:
            text = re.sub(pattern, "", text).strip()

        # Remove articles
        text = re.sub(r"^(the|a|an)\s+", "", text).strip()
        return text

    def _extract_query(self, text: str, keywords) -> str:
        text = text.lower().strip()
        for kw in keywords:
            if text.startswith(kw):
                return text[len(kw):].strip()
        return text
