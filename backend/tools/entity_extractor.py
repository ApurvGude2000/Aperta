"""
Entity Extraction Tool - Extracts structured entities from conversation text.
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json
import re


@dataclass
class Entity:
    """Represents an extracted entity."""
    entity_type: str  # person, company, topic, technology, action_item, date
    entity_value: str
    confidence: float
    context: str
    metadata: Dict[str, Any]
    start_pos: int = 0
    end_pos: int = 0


class EntityExtractor:
    """Extracts entities from conversation text using pattern matching and AI."""

    def __init__(self):
        """Initialize entity extractor."""
        # Common company indicators
        self.company_indicators = [
            'Inc.', 'LLC', 'Corp.', 'Corporation', 'Ltd.',
            'Limited', 'Co.', 'Company', 'Group', 'Technologies'
        ]

        # Technology keywords
        self.tech_keywords = [
            'API', 'SDK', 'AI', 'ML', 'cloud', 'database', 'framework',
            'platform', 'server', 'mobile', 'web', 'app', 'software',
            'Python', 'JavaScript', 'React', 'Node', 'AWS', 'Azure',
            'Docker', 'Kubernetes', 'TensorFlow', 'PyTorch'
        ]

        # Action item indicators
        self.action_indicators = [
            "i'll", "i will", "let me", "i can", "i should",
            "we'll", "we will", "let's", "we can", "we should",
            "send me", "email me", "call me", "contact me",
            "follow up", "reach out", "connect", "schedule"
        ]

    def extract_all(
        self,
        text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Entity]:
        """
        Extract all entities from text.

        Args:
            text: Text to analyze
            context: Optional context (conversation_id, etc.)

        Returns:
            List of extracted entities
        """
        entities = []

        # Extract different entity types
        entities.extend(self._extract_people(text))
        entities.extend(self._extract_companies(text))
        entities.extend(self._extract_topics(text))
        entities.extend(self._extract_technologies(text))
        entities.extend(self._extract_action_items(text))
        entities.extend(self._extract_dates(text))

        return entities

    def _extract_people(self, text: str) -> List[Entity]:
        """Extract person names from text."""
        entities = []

        # Pattern: "I'm [Name]" or "My name is [Name]"
        intro_patterns = [
            r"(?:i'm|i am|my name is|this is|call me)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)",
            r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)(?:,|\s+(?:from|at|with))",
        ]

        for pattern in intro_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                name = match.group(1).strip()

                # Filter out common false positives
                if len(name.split()) >= 2 and not any(
                    word.lower() in ['the', 'and', 'for', 'with']
                    for word in name.split()
                ):
                    context = self._get_context(text, match.start(), match.end())

                    entities.append(Entity(
                        entity_type='person',
                        entity_value=name,
                        confidence=0.85,
                        context=context,
                        metadata={'pattern': 'name_introduction'},
                        start_pos=match.start(),
                        end_pos=match.end()
                    ))

        return entities

    def _extract_companies(self, text: str) -> List[Entity]:
        """Extract company names from text."""
        entities = []

        # Pattern: Known companies or companies with indicators
        # First, extract known tech companies (common in networking)
        known_companies = [
            'Google', 'Microsoft', 'Amazon', 'Apple', 'Meta', 'Facebook',
            'Netflix', 'Tesla', 'SpaceX', 'Stripe', 'Airbnb', 'Uber',
            'OpenAI', 'Anthropic', 'DeepMind', 'NVIDIA', 'Intel', 'AMD'
        ]

        for company in known_companies:
            pattern = rf'\b{company}\b'
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                context = self._get_context(text, match.start(), match.end())
                entities.append(Entity(
                    entity_type='company',
                    entity_value=match.group(),
                    confidence=0.95,
                    context=context,
                    metadata={'source': 'known_company'},
                    start_pos=match.start(),
                    end_pos=match.end()
                ))

        # Pattern: Company with suffix (e.g., "Acme Inc.")
        for indicator in self.company_indicators:
            pattern = rf'([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)*)\s+{re.escape(indicator)}'
            matches = re.finditer(pattern, text)
            for match in matches:
                company_name = match.group(1) + ' ' + indicator
                context = self._get_context(text, match.start(), match.end())
                entities.append(Entity(
                    entity_type='company',
                    entity_value=company_name,
                    confidence=0.90,
                    context=context,
                    metadata={'source': 'suffix_indicator'},
                    start_pos=match.start(),
                    end_pos=match.end()
                ))

        return entities

    def _extract_topics(self, text: str) -> List[Entity]:
        """Extract discussion topics from text."""
        entities = []

        # Pattern: "about [topic]", "discussing [topic]", etc.
        topic_patterns = [
            r'(?:about|discuss(?:ing)?|regarding|concerning|on the topic of)\s+([a-z\s]+(?:opportunities|challenges|issues|strategies|plans|projects))',
            r'(?:interested in|looking for|focusing on)\s+([a-z\s]+(?:opportunities|positions|roles|internships))',
        ]

        for pattern in topic_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                topic = match.group(1).strip()
                context = self._get_context(text, match.start(), match.end())

                entities.append(Entity(
                    entity_type='topic',
                    entity_value=topic,
                    confidence=0.75,
                    context=context,
                    metadata={'extraction_method': 'pattern'},
                    start_pos=match.start(),
                    end_pos=match.end()
                ))

        return entities

    def _extract_technologies(self, text: str) -> List[Entity]:
        """Extract technology mentions from text."""
        entities = []

        for tech in self.tech_keywords:
            pattern = rf'\b{re.escape(tech)}\b'
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                context = self._get_context(text, match.start(), match.end())
                entities.append(Entity(
                    entity_type='technology',
                    entity_value=match.group(),
                    confidence=0.90,
                    context=context,
                    metadata={'category': 'technology'},
                    start_pos=match.start(),
                    end_pos=match.end()
                ))

        return entities

    def _extract_action_items(self, text: str) -> List[Entity]:
        """Extract action items and commitments from text."""
        entities = []

        # Split into sentences
        sentences = re.split(r'[.!?]+', text)

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            # Check if sentence contains action indicators
            for indicator in self.action_indicators:
                if indicator.lower() in sentence.lower():
                    # Extract the action
                    context = sentence[:100]  # Use full sentence as context

                    entities.append(Entity(
                        entity_type='action_item',
                        entity_value=sentence,
                        confidence=0.80,
                        context=context,
                        metadata={'indicator': indicator},
                        start_pos=text.find(sentence),
                        end_pos=text.find(sentence) + len(sentence)
                    ))
                    break  # Only add once per sentence

        return entities

    def _extract_dates(self, text: str) -> List[Entity]:
        """Extract dates and deadlines from text."""
        entities = []

        # Date patterns
        date_patterns = [
            r'\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|'
            r'Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)'
            r'\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}\b',
            r'\b\d{1,2}/\d{1,2}/\d{4}\b',
            r'\b\d{4}-\d{2}-\d{2}\b',
            r'\b(?:next|this)\s+(?:week|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
            r'\b(?:tomorrow|today|yesterday)\b',
        ]

        for pattern in date_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                date_str = match.group()
                context = self._get_context(text, match.start(), match.end())

                entities.append(Entity(
                    entity_type='date',
                    entity_value=date_str,
                    confidence=0.85,
                    context=context,
                    metadata={'format': 'date_string'},
                    start_pos=match.start(),
                    end_pos=match.end()
                ))

        return entities

    def _get_context(
        self,
        text: str,
        start: int,
        end: int,
        window: int = 50
    ) -> str:
        """Extract context around a match."""
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        context = text[context_start:context_end]

        # Add ellipsis
        if context_start > 0:
            context = '...' + context
        if context_end < len(text):
            context = context + '...'

        return context

    def resolve_entities(
        self,
        entities: List[Entity]
    ) -> Dict[str, List[Entity]]:
        """
        Resolve and group similar entities.

        Args:
            entities: List of extracted entities

        Returns:
            Dictionary grouped by canonical entity
        """
        resolved = {}

        # Group by type first
        by_type = {}
        for entity in entities:
            if entity.entity_type not in by_type:
                by_type[entity.entity_type] = []
            by_type[entity.entity_type].append(entity)

        # Resolve within each type
        for entity_type, type_entities in by_type.items():
            if entity_type == 'person':
                resolved[entity_type] = self._resolve_people(type_entities)
            elif entity_type == 'company':
                resolved[entity_type] = self._resolve_companies(type_entities)
            else:
                resolved[entity_type] = type_entities

        return resolved

    def _resolve_people(self, entities: List[Entity]) -> List[Entity]:
        """Resolve person name variations (e.g., 'John' and 'John Smith')."""
        # Group by full name match
        unique = {}
        for entity in entities:
            name = entity.entity_value.lower()
            # Keep the longest version of similar names
            found = False
            for existing_name in list(unique.keys()):
                if name in existing_name or existing_name in name:
                    # Keep the longer name
                    if len(name) > len(existing_name):
                        unique[name] = entity
                        del unique[existing_name]
                    found = True
                    break
            if not found:
                unique[name] = entity

        return list(unique.values())

    def _resolve_companies(self, entities: List[Entity]) -> List[Entity]:
        """Resolve company name variations."""
        # Simple deduplication by exact match (case-insensitive)
        unique = {}
        for entity in entities:
            key = entity.entity_value.lower()
            if key not in unique:
                unique[key] = entity

        return list(unique.values())

    def to_json(self, entities: List[Entity]) -> List[Dict[str, Any]]:
        """Convert entities to JSON-serializable format."""
        return [
            {
                'type': entity.entity_type,
                'value': entity.entity_value,
                'confidence': entity.confidence,
                'context': entity.context,
                'metadata': entity.metadata,
                'position': {'start': entity.start_pos, 'end': entity.end_pos}
            }
            for entity in entities
        ]

    def get_statistics(self, entities: List[Entity]) -> Dict[str, Any]:
        """Get statistics about extracted entities."""
        stats = {
            'total': len(entities),
            'by_type': {},
            'high_confidence': 0,
            'medium_confidence': 0,
            'low_confidence': 0
        }

        for entity in entities:
            # Count by type
            entity_type = entity.entity_type
            stats['by_type'][entity_type] = stats['by_type'].get(entity_type, 0) + 1

            # Count by confidence
            if entity.confidence >= 0.85:
                stats['high_confidence'] += 1
            elif entity.confidence >= 0.70:
                stats['medium_confidence'] += 1
            else:
                stats['low_confidence'] += 1

        return stats


# Convenience function
def extract_entities(text: str) -> List[Dict[str, Any]]:
    """
    Quick function to extract entities from text.

    Args:
        text: Text to analyze

    Returns:
        List of entities as dictionaries
    """
    extractor = EntityExtractor()
    entities = extractor.extract_all(text)
    return extractor.to_json(entities)
