"""Duplicate detection service using TF-IDF similarity."""
import hashlib
import re
from typing import Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

from app.repositories.issue import IssueRepository


class DuplicateDetectionService:
    """
    Service for detecting duplicate issues using TF-IDF similarity.

    Uses scikit-learn's TfidfVectorizer for text vectorization
    and cosine similarity for matching.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.issue_repo = IssueRepository(db)

        if SKLEARN_AVAILABLE:
            self.vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words="english",
                ngram_range=(1, 2),
                lowercase=True,
            )
        else:
            self.vectorizer = None

    def generate_deduplication_hash(
        self,
        title: str,
        description: Optional[str] = None,
    ) -> str:
        """
        Generate a SHA256 hash for deduplication.

        Normalizes the text before hashing for consistent results.
        """
        # Normalize title
        normalized_title = self._normalize_text(title)

        # Normalize description
        normalized_desc = ""
        if description:
            normalized_desc = self._normalize_text(description)

        # Combine and hash
        combined = f"{normalized_title}|{normalized_desc}"
        return hashlib.sha256(combined.encode()).hexdigest()

    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison."""
        # Lowercase
        text = text.lower().strip()

        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text)

        # Remove special characters except alphanumeric and spaces
        text = re.sub(r"[^a-z0-9\s]", "", text)

        return text

    async def find_similar_issues(
        self,
        project_id: str,
        title: str,
        description: Optional[str] = None,
        threshold: float = 0.3,
        limit: int = 5,
    ) -> List[Dict]:
        """
        Find similar issues in a project using TF-IDF similarity.

        Args:
            project_id: Project to search within
            title: Title of new issue
            description: Description of new issue
            threshold: Minimum similarity score (0-1)
            limit: Maximum number of results

        Returns:
            List of similar issues with similarity scores
        """
        # Get existing open issues in project
        existing_issues = await self.issue_repo.get_open_issues_for_project(project_id)

        if not existing_issues:
            return []

        if not SKLEARN_AVAILABLE:
            # Fallback to simple keyword matching if sklearn not available
            return self._simple_keyword_match(
                existing_issues,
                title,
                description,
                limit,
            )

        # Build corpus from existing issues
        corpus = []
        for issue in existing_issues:
            text = f"{issue.title} {issue.description or ''}"
            corpus.append(text)

        # Add new issue text
        new_text = f"{title} {description or ''}"
        corpus.append(new_text)

        # Vectorize all texts
        try:
            tfidf_matrix = self.vectorizer.fit_transform(corpus)
        except ValueError:
            # Empty corpus or all stop words
            return []

        # Calculate similarity between new issue and all existing
        new_vector = tfidf_matrix[-1:]
        existing_vectors = tfidf_matrix[:-1]

        similarities = cosine_similarity(new_vector, existing_vectors)[0]

        # Get top matches above threshold
        results = []
        for idx, score in enumerate(similarities):
            if score >= threshold:
                results.append({
                    "issue": existing_issues[idx],
                    "similarity_score": int(score * 100),  # Convert to percentage
                })

        # Sort by score descending and limit
        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        return results[:limit]

    def _simple_keyword_match(
        self,
        issues: List,
        title: str,
        description: Optional[str],
        limit: int,
    ) -> List[Dict]:
        """Fallback keyword matching when sklearn is not available."""
        # Extract keywords from new issue
        new_text = f"{title} {description or ''}".lower()
        new_words = set(re.findall(r"\b\w+\b", new_text))

        # Remove common words
        stop_words = {"the", "a", "an", "is", "are", "was", "were", "be", "been",
                      "being", "have", "has", "had", "do", "does", "did", "will",
                      "would", "could", "should", "may", "might", "must", "shall",
                      "can", "need", "dare", "ought", "used", "to", "of", "in",
                      "for", "on", "with", "at", "by", "from", "as", "into",
                      "through", "during", "before", "after", "above", "below",
                      "between", "under", "again", "further", "then", "once",
                      "and", "but", "or", "nor", "so", "yet", "both", "either",
                      "neither", "not", "only", "own", "same", "than", "too",
                      "very", "just", "also", "now", "here", "there", "when",
                      "where", "why", "how", "all", "each", "every", "both",
                      "few", "more", "most", "other", "some", "such", "no",
                      "any", "this", "that", "these", "those", "it", "its"}

        new_words = new_words - stop_words

        results = []
        for issue in issues:
            issue_text = f"{issue.title} {issue.description or ''}".lower()
            issue_words = set(re.findall(r"\b\w+\b", issue_text)) - stop_words

            # Calculate Jaccard similarity
            if not new_words or not issue_words:
                continue

            intersection = len(new_words & issue_words)
            union = len(new_words | issue_words)
            similarity = intersection / union if union > 0 else 0

            if similarity >= 0.2:  # 20% threshold
                results.append({
                    "issue": issue,
                    "similarity_score": int(similarity * 100),
                })

        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        return results[:limit]
