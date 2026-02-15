"""
Intent Recognition Tool - Identifies user's networking goals and intentions.
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import re


class IntentType(str, Enum):
    """Types of networking intents."""
    JOB_SEEKING = "job_seeking"
    FUNDRAISING = "fundraising"
    PARTNERSHIP = "partnership"
    LEARNING = "learning"
    HIRING = "hiring"
    SELLING = "selling"
    GENERAL_NETWORKING = "general_networking"
    MENTORSHIP = "mentorship"
    CAREER_ADVICE = "career_advice"
    COLLABORATION = "collaboration"


@dataclass
class Intent:
    """Represents a detected intent."""
    intent_type: IntentType
    confidence: float
    evidence: List[str]  # Text snippets that support this intent
    keywords: List[str]  # Keywords that triggered detection
    metadata: Dict[str, Any]


class IntentRecognizer:
    """Recognizes user's networking intentions from conversation."""

    def __init__(self):
        """Initialize intent recognizer with keyword patterns."""

        # Intent keyword mappings
        self.intent_patterns = {
            IntentType.JOB_SEEKING: {
                'keywords': [
                    'looking for', 'job', 'position', 'role', 'opportunity',
                    'hiring', 'applying', 'career', 'employment', 'opening',
                    'intern', 'internship', 'full-time', 'part-time',
                    'resume', 'cv', 'interview', 'candidate'
                ],
                'phrases': [
                    'looking for a job', 'seeking opportunities',
                    'interested in positions', 'want to work',
                    'applying for', 'career opportunities'
                ]
            },

            IntentType.FUNDRAISING: {
                'keywords': [
                    'fundraising', 'investor', 'funding', 'capital',
                    'seed round', 'series a', 'series b', 'venture',
                    'investment', 'raise', 'pitch', 'valuation'
                ],
                'phrases': [
                    'raising capital', 'seeking investors',
                    'looking for funding', 'pitch deck',
                    'fundraising round'
                ]
            },

            IntentType.PARTNERSHIP: {
                'keywords': [
                    'partner', 'partnership', 'collaborate', 'collaboration',
                    'joint venture', 'alliance', 'co-founder', 'business development'
                ],
                'phrases': [
                    'looking for partners', 'potential collaboration',
                    'work together', 'business partnership',
                    'strategic alliance'
                ]
            },

            IntentType.LEARNING: {
                'keywords': [
                    'learn', 'learning', 'understand', 'know more',
                    'interested in', 'curious', 'explore', 'discover',
                    'information', 'insights', 'knowledge'
                ],
                'phrases': [
                    'want to learn', 'interested in learning',
                    'know more about', 'understand how',
                    'learning about'
                ]
            },

            IntentType.HIRING: {
                'keywords': [
                    'hiring', 'recruit', 'recruiting', 'talent',
                    'team', 'join our team', 'looking for candidates',
                    'open positions', 'job openings'
                ],
                'phrases': [
                    'we are hiring', "we're hiring", 'looking for talent',
                    'recruiting for', 'join our team',
                    'open positions'
                ]
            },

            IntentType.SELLING: {
                'keywords': [
                    'sell', 'selling', 'product', 'service', 'solution',
                    'offer', 'provide', 'demo', 'trial', 'pricing'
                ],
                'phrases': [
                    'we offer', 'our product', 'our service',
                    'can help with', 'solution for'
                ]
            },

            IntentType.MENTORSHIP: {
                'keywords': [
                    'mentor', 'mentorship', 'advice', 'guidance',
                    'coach', 'coaching', 'help', 'support'
                ],
                'phrases': [
                    'looking for a mentor', 'seeking mentorship',
                    'need advice', 'guidance on',
                    'mentor someone'
                ]
            },

            IntentType.CAREER_ADVICE: {
                'keywords': [
                    'career', 'advice', 'guidance', 'direction',
                    'path', 'transition', 'change', 'next step'
                ],
                'phrases': [
                    'career advice', 'career path', 'career transition',
                    'next step in my career', 'career guidance'
                ]
            },

            IntentType.COLLABORATION: {
                'keywords': [
                    'collaborate', 'collaboration', 'work together',
                    'project', 'research', 'joint', 'team up'
                ],
                'phrases': [
                    'work together on', 'collaborate on',
                    'joint project', 'research collaboration',
                    'team up for'
                ]
            }
        }

    def recognize(
        self,
        text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Intent]:
        """
        Recognize intents from text.

        Args:
            text: Text to analyze
            context: Optional context information

        Returns:
            List of detected intents sorted by confidence
        """
        text_lower = text.lower()
        detected_intents = []

        # Check each intent type
        for intent_type, patterns in self.intent_patterns.items():
            score = 0
            evidence = []
            found_keywords = []

            # Check keywords
            for keyword in patterns['keywords']:
                if keyword.lower() in text_lower:
                    score += 1
                    found_keywords.append(keyword)

                    # Extract evidence snippet
                    evidence_snippet = self._extract_evidence(text, keyword)
                    if evidence_snippet:
                        evidence.append(evidence_snippet)

            # Check phrases (worth more)
            for phrase in patterns['phrases']:
                if phrase.lower() in text_lower:
                    score += 3
                    found_keywords.append(phrase)

                    # Extract evidence snippet
                    evidence_snippet = self._extract_evidence(text, phrase)
                    if evidence_snippet:
                        evidence.append(evidence_snippet)

            # Calculate confidence
            if score > 0:
                # Normalize confidence (max 10 points possible per intent)
                confidence = min(score / 10.0, 1.0)

                # Boost confidence if multiple strong signals
                if len(evidence) > 2:
                    confidence = min(confidence * 1.2, 1.0)

                detected_intents.append(Intent(
                    intent_type=intent_type,
                    confidence=confidence,
                    evidence=evidence[:5],  # Keep top 5 evidence snippets
                    keywords=list(set(found_keywords))[:10],  # Keep top 10 unique keywords
                    metadata={
                        'score': score,
                        'keyword_matches': len(found_keywords)
                    }
                ))

        # Sort by confidence
        detected_intents.sort(key=lambda x: x.confidence, reverse=True)

        # If no specific intent detected, assign general networking
        if not detected_intents:
            detected_intents.append(Intent(
                intent_type=IntentType.GENERAL_NETWORKING,
                confidence=0.5,
                evidence=['No specific intent detected'],
                keywords=[],
                metadata={'default': True}
            ))

        return detected_intents

    def _extract_evidence(
        self,
        text: str,
        keyword: str,
        window: int = 60
    ) -> Optional[str]:
        """Extract evidence snippet around keyword."""
        text_lower = text.lower()
        keyword_lower = keyword.lower()

        # Find keyword position
        pos = text_lower.find(keyword_lower)
        if pos == -1:
            return None

        # Extract context
        start = max(0, pos - window)
        end = min(len(text), pos + len(keyword) + window)

        snippet = text[start:end].strip()

        # Add ellipsis
        if start > 0:
            snippet = '...' + snippet
        if end < len(text):
            snippet = snippet + '...'

        return snippet

    def get_primary_intent(
        self,
        text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Intent:
        """
        Get the primary (highest confidence) intent.

        Args:
            text: Text to analyze
            context: Optional context

        Returns:
            Primary intent
        """
        intents = self.recognize(text, context)
        return intents[0] if intents else Intent(
            intent_type=IntentType.GENERAL_NETWORKING,
            confidence=0.5,
            evidence=[],
            keywords=[],
            metadata={}
        )

    def get_intent_summary(
        self,
        text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get a summary of all detected intents.

        Args:
            text: Text to analyze
            context: Optional context

        Returns:
            Summary dictionary with intents and statistics
        """
        intents = self.recognize(text, context)

        summary = {
            'primary_intent': intents[0].intent_type.value if intents else 'unknown',
            'primary_confidence': intents[0].confidence if intents else 0.0,
            'all_intents': [
                {
                    'type': intent.intent_type.value,
                    'confidence': intent.confidence,
                    'evidence_count': len(intent.evidence),
                    'keyword_count': len(intent.keywords)
                }
                for intent in intents
            ],
            'intent_count': len(intents),
            'high_confidence_count': len([i for i in intents if i.confidence >= 0.7]),
            'text_length': len(text)
        }

        return summary

    def to_json(self, intents: List[Intent]) -> List[Dict[str, Any]]:
        """Convert intents to JSON-serializable format."""
        return [
            {
                'type': intent.intent_type.value,
                'confidence': intent.confidence,
                'evidence': intent.evidence,
                'keywords': intent.keywords,
                'metadata': intent.metadata
            }
            for intent in intents
        ]


# Convenience function
def recognize_intent(text: str) -> Dict[str, Any]:
    """
    Quick function to recognize intent from text.

    Args:
        text: Text to analyze

    Returns:
        Intent summary as dictionary
    """
    recognizer = IntentRecognizer()
    return recognizer.get_intent_summary(text)
