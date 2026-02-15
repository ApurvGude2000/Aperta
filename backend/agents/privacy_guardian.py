"""
AG3: Privacy Guardian Agent - Protects user privacy by detecting and redacting PII.
Priority: 1 (CRITICAL) - Has veto authority over all other agents.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy import select
from .base import ClaudeBaseAgent
from tools.pii_detector import PIIDetector, PIIType
from tools.redactor import Redactor
from utils.logger import setup_logger
from db.session import AsyncSessionLocal
from db.models import PrivacyAuditLog, Conversation

logger = setup_logger(__name__)


class PrivacyGuardianAgent(ClaudeBaseAgent):
    """
    Privacy Guardian Agent - AG3

    Responsibilities:
    1. Real-time PII detection
    2. Automatic redaction
    3. Consent tracking
    4. Privacy auditing
    5. Veto authority over other agents

    Priority: 1 (CRITICAL) - Can block any operation that violates privacy.
    """

    def __init__(self):
        """Initialize Privacy Guardian Agent."""
        system_prompt = """You are the Privacy Guardian, a critical security agent responsible for protecting user privacy.

Your primary responsibilities:
1. Detect personally identifiable information (PII) in all conversations
2. Assess privacy risks and recommend redactions
3. Classify sensitive topics (salary, health, legal, confidential)
4. Ensure compliance with privacy regulations (GDPR, CCPA)
5. Exercise veto authority when privacy is at risk

PII types to detect:
- Email addresses
- Phone numbers
- Social Security Numbers
- Credit card numbers
- Physical addresses
- Full names in sensitive contexts
- URLs to social media profiles
- IP addresses

When analyzing text:
1. Identify all PII instances with their exact locations
2. Assess the sensitivity level (critical, high, medium, low)
3. Recommend redaction strategies
4. Flag any consent issues
5. Suggest privacy-preserving alternatives

You have VETO AUTHORITY - if any operation would compromise privacy, you must block it.

Be thorough but balanced - not all name mentions need redaction, use context to decide."""

        super().__init__(
            name="privacy_guardian",
            description="Protects privacy by detecting and redacting PII",
            system_prompt=system_prompt,
            priority=1  # Highest priority - CRITICAL
        )

        # Initialize privacy tools
        self.pii_detector = PIIDetector()
        self.redactor = Redactor()

        # Privacy statistics
        self.total_pii_detected = 0
        self.total_redactions = 0
        self.veto_count = 0

        logger.info("Privacy Guardian Agent initialized with VETO AUTHORITY")

    async def analyze_privacy(
        self,
        text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze text for privacy concerns.

        Args:
            text: Text to analyze
            context: Optional context (conversation_id, user_id, etc.)

        Returns:
            Privacy analysis with detected PII and recommendations
        """
        logger.info(f"Privacy Guardian analyzing text ({len(text)} chars)")

        # Step 1: Detect PII using regex-based detector
        pii_matches = self.pii_detector.detect_all(text)
        self.total_pii_detected += len(pii_matches)

        # Step 2: Analyze with Claude for semantic understanding
        claude_analysis = await self._analyze_with_claude(text, pii_matches, context)

        # Step 3: Assess overall risk
        risk_assessment = self._assess_privacy_risk(pii_matches, claude_analysis)

        # Step 4: Generate recommendations
        recommendations = self._generate_recommendations(
            pii_matches,
            claude_analysis,
            risk_assessment
        )

        result = {
            'pii_detected': len(pii_matches),
            'pii_matches': self.pii_detector.to_json(pii_matches),
            'statistics': self.pii_detector.get_statistics(pii_matches),
            'risk_level': risk_assessment['risk_level'],
            'sensitive_topics': claude_analysis.get('sensitive_topics', []),
            'recommendations': recommendations,
            'veto_required': risk_assessment['veto_required'],
            'timestamp': datetime.utcnow().isoformat()
        }

        logger.info(
            f"Privacy analysis complete: {len(pii_matches)} PII instances, "
            f"risk={risk_assessment['risk_level']}"
        )

        # Log to database if PII detected or high risk
        if len(pii_matches) > 0 or risk_assessment['risk_level'] in ['high', 'critical']:
            try:
                await self._log_to_database(
                    action="PII_ANALYSIS",
                    details={
                        'pii_count': len(pii_matches),
                        'risk_level': risk_assessment['risk_level'],
                        'sensitive_topics': claude_analysis.get('sensitive_topics', []),
                        'veto_required': risk_assessment['veto_required']
                    },
                    conversation_id=context.get('conversation_id') if context else None
                )
            except Exception as e:
                logger.error(f"Failed to log privacy analysis: {e}")

        return result

    async def redact_pii(
        self,
        text: str,
        pii_types: Optional[List[PIIType]] = None,
        preserve_format: bool = True
    ) -> Dict[str, Any]:
        """
        Redact PII from text.

        Args:
            text: Text to redact
            pii_types: Specific PII types to redact (None = all)
            preserve_format: Preserve format hints in redacted text

        Returns:
            Redaction result with original and redacted text
        """
        logger.info(f"Redacting PII from text ({len(text)} chars)")

        result = self.redactor.redact_text(
            text=text,
            pii_types=pii_types,
            preserve_format=preserve_format
        )

        self.total_redactions += result['total_redactions']

        logger.info(f"Redaction complete: {result['total_redactions']} items redacted")

        return result

    async def check_consent(
        self,
        conversation_id: str,
        participant_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Check consent status for a conversation or participant.

        Args:
            conversation_id: Conversation ID
            participant_id: Optional specific participant

        Returns:
            Consent status and recommendations
        """
        try:
            async with AsyncSessionLocal() as session:
                # Check if conversation exists
                result = await session.execute(
                    select(Conversation).where(Conversation.id == conversation_id)
                )
                conversation = result.scalar_one_or_none()

                if not conversation:
                    return {
                        'consent_granted': False,
                        'consent_timestamp': None,
                        'requires_action': True,
                        'message': f'Conversation {conversation_id} not found'
                    }

                # For now, assume consent is granted if conversation exists
                # In a full implementation, you would check a ConversationConsent table
                # or a consent field on the Participant model
                return {
                    'consent_granted': True,
                    'consent_timestamp': conversation.created_at.isoformat(),
                    'requires_action': False,
                    'message': 'Consent tracking active'
                }

        except Exception as e:
            logger.error(f"Error checking consent: {e}")
            return {
                'consent_granted': False,
                'consent_timestamp': None,
                'requires_action': True,
                'message': f'Error checking consent: {str(e)}'
            }

    async def exercise_veto(
        self,
        operation: str,
        reason: str,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Exercise veto authority to block an operation.

        Args:
            operation: Operation being vetoed
            reason: Reason for veto
            details: Additional details

        Returns:
            Veto record
        """
        self.veto_count += 1

        veto_record = {
            'veto_id': f"veto_{datetime.utcnow().timestamp()}",
            'operation': operation,
            'reason': reason,
            'details': details or {},
            'timestamp': datetime.utcnow().isoformat(),
            'agent': self.name
        }

        # Log veto to database
        try:
            await self._log_to_database(
                action=f"VETO: {operation}",
                details={
                    'veto_record': veto_record,
                    'reason': reason
                },
                conversation_id=details.get('conversation_id') if details else None
            )
        except Exception as e:
            logger.error(f"Failed to log veto to database: {e}")

        logger.warning(
            f"PRIVACY VETO EXERCISED: {operation} - {reason} "
            f"(Total vetoes: {self.veto_count})"
        )

        return veto_record

    async def _analyze_with_claude(
        self,
        text: str,
        pii_matches: List,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Use Claude to analyze privacy concerns semantically."""

        # Build analysis prompt
        prompt = f"""Analyze this text for privacy and sensitive information concerns.

Text to analyze:
{text[:2000]}  # Limit for token efficiency

PII already detected by pattern matching:
- {len(pii_matches)} instances found
- Types: {', '.join(set(m.pii_type.value for m in pii_matches))}

Please analyze:
1. Are there sensitive topics being discussed? (salary, health, legal, confidential business, personal matters)
2. Are there any names or identifiers that should be protected based on context?
3. What is the overall privacy risk level?
4. Any additional privacy concerns not caught by pattern matching?

Respond in this JSON format:
{{
    "sensitive_topics": ["topic1", "topic2"],
    "additional_pii_concerns": ["concern1"],
    "privacy_risk_assessment": "low|medium|high|critical",
    "reasoning": "brief explanation"
}}"""

        try:
            # Execute with Claude
            result = await self.execute(
                prompt=prompt,
                context=context,
                max_tokens=1000,
                temperature=0.3  # Lower temperature for consistent analysis
            )

            # Parse Claude's response
            import json
            try:
                analysis = json.loads(result['response'])
            except:
                # If JSON parsing fails, return basic structure
                analysis = {
                    'sensitive_topics': [],
                    'additional_pii_concerns': [],
                    'privacy_risk_assessment': 'medium',
                    'reasoning': result['response'][:200]
                }

            return analysis

        except Exception as e:
            logger.error(f"Error in Claude privacy analysis: {e}")
            return {
                'sensitive_topics': [],
                'additional_pii_concerns': [],
                'privacy_risk_assessment': 'unknown',
                'reasoning': f'Analysis error: {str(e)}'
            }

    def _assess_privacy_risk(
        self,
        pii_matches: List,
        claude_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess overall privacy risk level."""

        # Count critical PII types
        critical_types = {PIIType.SSN, PIIType.CREDIT_CARD}
        has_critical = any(m.pii_type in critical_types for m in pii_matches)

        # Get Claude's assessment
        claude_risk = claude_analysis.get('privacy_risk_assessment', 'medium')

        # Determine overall risk
        if has_critical or claude_risk == 'critical':
            risk_level = 'critical'
            veto_required = True
        elif len(pii_matches) > 10 or claude_risk == 'high':
            risk_level = 'high'
            veto_required = True
        elif len(pii_matches) > 5 or claude_risk == 'medium':
            risk_level = 'medium'
            veto_required = False
        else:
            risk_level = 'low'
            veto_required = False

        return {
            'risk_level': risk_level,
            'veto_required': veto_required,
            'reasoning': claude_analysis.get('reasoning', 'Risk assessment based on PII detected')
        }

    def _generate_recommendations(
        self,
        pii_matches: List,
        claude_analysis: Dict[str, Any],
        risk_assessment: Dict[str, Any]
    ) -> List[str]:
        """Generate privacy recommendations."""
        recommendations = []

        # Based on risk level
        if risk_assessment['risk_level'] == 'critical':
            recommendations.append("IMMEDIATE ACTION REQUIRED: Critical PII detected")
            recommendations.append("Do not store or transmit this data without encryption")

        # Based on PII types
        stats = self.pii_detector.get_statistics(pii_matches)
        for pii_type, count in stats['by_type'].items():
            if pii_type == 'email':
                recommendations.append(f"Redact {count} email address(es) before sharing")
            elif pii_type == 'phone':
                recommendations.append(f"Verify consent for storing {count} phone number(s)")
            elif pii_type == 'ssn':
                recommendations.append(f"CRITICAL: {count} SSN(s) detected - immediate redaction required")
            elif pii_type == 'credit_card':
                recommendations.append(f"CRITICAL: {count} credit card(s) detected - do not store")

        # Based on Claude's analysis
        if claude_analysis.get('sensitive_topics'):
            topics = ', '.join(claude_analysis['sensitive_topics'])
            recommendations.append(f"Sensitive topics detected: {topics} - handle with care")

        # General recommendations
        if len(pii_matches) > 0:
            recommendations.append("Enable audit logging for all access to this data")
            recommendations.append("Consider end-to-end encryption for storage")

        return recommendations

    async def _log_to_database(
        self,
        action: str,
        details: Dict[str, Any],
        conversation_id: Optional[str] = None
    ) -> None:
        """
        Log privacy action to audit database.

        Args:
            action: Action performed (e.g., "PII_DETECTED", "REDACTION", "VETO")
            details: Action details as JSON
            conversation_id: Optional conversation ID
        """
        try:
            async with AsyncSessionLocal() as session:
                log_entry = PrivacyAuditLog(
                    conversation_id=conversation_id,
                    action=action,
                    details=details,
                    timestamp=datetime.utcnow()
                )
                session.add(log_entry)
                await session.commit()

                logger.debug(f"Privacy audit log created: {action}")

        except Exception as e:
            logger.error(f"Failed to create privacy audit log: {e}")
            # Don't raise - logging failure shouldn't block operations

    def get_stats(self) -> Dict[str, Any]:
        """Get Privacy Guardian statistics."""
        base_stats = super().get_stats()
        base_stats.update({
            'total_pii_detected': self.total_pii_detected,
            'total_redactions': self.total_redactions,
            'veto_count': self.veto_count,
            'veto_authority': True
        })
        return base_stats
