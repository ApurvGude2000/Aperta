"""
AG2: Perception Agent - Monitors input and manages system resources.
Priority: 4 - System monitoring and resource management.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum
import psutil
import asyncio
from .base import ClaudeBaseAgent
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ConversationState(str, Enum):
    """Conversation states."""
    IDLE = "idle"
    ACTIVE = "active"
    PROCESSING = "processing"
    PAUSED = "paused"


class PerceptionAgent(ClaudeBaseAgent):
    """
    Perception Agent - AG2

    Responsibilities:
    1. Monitor user input (text, file uploads, audio transcription)
    2. Detect conversation start/stop
    3. Manage system resources (CPU, memory, API rate limits)
    4. Implement adaptive sampling logic
    5. Send state change notifications
    6. Track user patterns for optimization

    Priority: 4 - System monitoring and resource management.

    Note: For web app, focuses on input monitoring rather than physical sensors.
    """

    def __init__(self):
        """Initialize Perception Agent."""
        system_prompt = """You are the Perception Agent, responsible for monitoring system state and resources.

Your primary responsibilities:
1. Monitor user input and conversation activity
2. Detect when conversations start and end
3. Manage system resources to ensure smooth operation
4. Adapt processing intensity based on activity
5. Provide notifications about state changes
6. Learn user patterns to optimize performance

States to track:
- IDLE: No active conversation
- ACTIVE: Conversation in progress
- PROCESSING: Analyzing conversation data
- PAUSED: Temporarily paused (privacy, resource constraints)

Resource management:
- Monitor CPU and memory usage
- Track API rate limits (Claude API calls)
- Throttle processing when resources are constrained
- Queue tasks during high load

Adaptive sampling:
- Increase monitoring frequency during active conversations
- Decrease during idle periods
- Adjust based on conversation complexity and importance

Be proactive but efficient - optimize for performance and cost."""

        super().__init__(
            name="perception",
            description="Monitors input and manages system resources",
            system_prompt=system_prompt,
            priority=4  # Lower priority - system management
        )

        # State tracking
        self.current_state = ConversationState.IDLE
        self.state_history: List[Dict[str, Any]] = []
        self.last_activity = datetime.utcnow()

        # Resource tracking
        self.api_calls_count = 0
        self.api_calls_limit = 100  # Per hour
        self.api_calls_reset_time = datetime.utcnow() + timedelta(hours=1)

        # Statistics
        self.total_state_changes = 0
        self.total_notifications_sent = 0
        self.total_resource_warnings = 0
        self.idle_time_seconds = 0
        self.active_time_seconds = 0

        logger.info("Perception Agent initialized")

    async def monitor_input(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Monitor user input and update state.

        Args:
            input_data: Input data (text, file, audio)
            context: Optional context

        Returns:
            Monitoring result with state and recommendations
        """
        input_type = input_data.get('type', 'unknown')
        content_length = len(str(input_data.get('content', '')))

        logger.info(f"Monitoring input: type={input_type}, length={content_length}")

        self.last_activity = datetime.utcnow()

        # Determine if this represents conversation activity
        is_conversation_input = (
            input_type in ['text', 'audio_transcription', 'file_transcript'] and
            content_length > 50  # Minimum threshold for meaningful input
        )

        if is_conversation_input:
            # Transition to ACTIVE if not already
            if self.current_state == ConversationState.IDLE:
                await self._change_state(ConversationState.ACTIVE)

        # Check resource availability
        resource_status = await self.check_resources()

        # Adaptive sampling recommendation
        sampling_rate = self._calculate_sampling_rate(
            state=self.current_state,
            input_type=input_type,
            resource_status=resource_status
        )

        return {
            'current_state': self.current_state.value,
            'input_processed': True,
            'is_conversation': is_conversation_input,
            'resource_status': resource_status,
            'sampling_rate': sampling_rate,
            'last_activity': self.last_activity.isoformat(),
            'recommendations': self._generate_recommendations(resource_status)
        }

    async def detect_conversation_state(
        self,
        conversation_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Detect conversation start/stop/pause.

        Args:
            conversation_data: Conversation information
            context: Optional context

        Returns:
            State detection result
        """
        logger.info("Detecting conversation state")

        # Check for inactivity timeout
        time_since_activity = (datetime.utcnow() - self.last_activity).total_seconds()
        inactivity_threshold = 300  # 5 minutes

        if time_since_activity > inactivity_threshold and self.current_state == ConversationState.ACTIVE:
            # Auto-transition to IDLE
            await self._change_state(ConversationState.IDLE)
            return {
                'state': ConversationState.IDLE.value,
                'reason': 'inactivity_timeout',
                'time_inactive': time_since_activity
            }

        # Check for explicit state signals
        explicit_state = conversation_data.get('explicit_state')
        if explicit_state:
            if explicit_state == 'start':
                await self._change_state(ConversationState.ACTIVE)
            elif explicit_state == 'stop':
                await self._change_state(ConversationState.IDLE)
            elif explicit_state == 'pause':
                await self._change_state(ConversationState.PAUSED)

        return {
            'state': self.current_state.value,
            'time_since_activity': time_since_activity,
            'auto_idle_threshold': inactivity_threshold
        }

    async def check_resources(self) -> Dict[str, Any]:
        """
        Check system resource availability.

        Returns:
            Resource status report
        """
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.1)

            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent

            # Disk usage (for logs, database)
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent

            # API rate limit check
            if datetime.utcnow() > self.api_calls_reset_time:
                self.api_calls_count = 0
                self.api_calls_reset_time = datetime.utcnow() + timedelta(hours=1)

            api_calls_remaining = self.api_calls_limit - self.api_calls_count

            # Overall status
            status = 'healthy'
            if cpu_percent > 80 or memory_percent > 85 or api_calls_remaining < 10:
                status = 'constrained'
                self.total_resource_warnings += 1
            elif cpu_percent > 90 or memory_percent > 95 or api_calls_remaining < 5:
                status = 'critical'
                self.total_resource_warnings += 1

            return {
                'status': status,
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'disk_percent': disk_percent,
                'api_calls_remaining': api_calls_remaining,
                'api_calls_limit': self.api_calls_limit,
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error checking resources: {e}")
            return {
                'status': 'unknown',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    async def notify_state_change(
        self,
        new_state: ConversationState,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send notification about state change.

        Args:
            new_state: New conversation state
            reason: Optional reason for change

        Returns:
            Notification details
        """
        self.total_notifications_sent += 1

        notification = {
            'type': 'state_change',
            'previous_state': self.current_state.value,
            'new_state': new_state.value,
            'reason': reason or 'automatic',
            'timestamp': datetime.utcnow().isoformat(),
            'notification_id': f"notif_{datetime.utcnow().timestamp()}"
        }

        logger.info(
            f"State change notification: {self.current_state.value} → {new_state.value}"
        )

        return notification

    def _calculate_sampling_rate(
        self,
        state: ConversationState,
        input_type: str,
        resource_status: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate adaptive sampling rate."""

        base_rates = {
            ConversationState.IDLE: 10,      # Check every 10 seconds
            ConversationState.ACTIVE: 2,     # Check every 2 seconds
            ConversationState.PROCESSING: 5, # Check every 5 seconds
            ConversationState.PAUSED: 30     # Check every 30 seconds
        }

        base_rate = base_rates.get(state, 10)

        # Adjust based on resources
        if resource_status.get('status') == 'constrained':
            base_rate *= 2  # Reduce frequency
        elif resource_status.get('status') == 'critical':
            base_rate *= 4  # Significantly reduce

        return {
            'interval_seconds': base_rate,
            'state': state.value,
            'adjusted_for_resources': resource_status.get('status') != 'healthy'
        }

    def _generate_recommendations(
        self,
        resource_status: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on resource status."""
        recommendations = []

        if resource_status.get('cpu_percent', 0) > 80:
            recommendations.append("High CPU usage - consider reducing processing frequency")

        if resource_status.get('memory_percent', 0) > 85:
            recommendations.append("High memory usage - consider freeing resources")

        if resource_status.get('api_calls_remaining', 100) < 10:
            recommendations.append("API rate limit approaching - queue non-urgent requests")

        if resource_status.get('status') == 'critical':
            recommendations.append("CRITICAL: System resources constrained - pause non-essential processing")

        return recommendations

    async def _change_state(
        self,
        new_state: ConversationState,
        reason: Optional[str] = None
    ) -> None:
        """Change conversation state and record history."""
        if new_state == self.current_state:
            return  # No change

        old_state = self.current_state
        self.current_state = new_state
        self.total_state_changes += 1

        # Record in history
        self.state_history.append({
            'from_state': old_state.value,
            'to_state': new_state.value,
            'reason': reason,
            'timestamp': datetime.utcnow().isoformat()
        })

        # Keep last 100 state changes
        if len(self.state_history) > 100:
            self.state_history = self.state_history[-100:]

        # Send notification
        await self.notify_state_change(new_state, reason)

        # Update time tracking
        if new_state == ConversationState.IDLE:
            # Switched to idle
            pass
        elif new_state == ConversationState.ACTIVE:
            # Switched to active
            pass

        logger.info(f"State changed: {old_state.value} → {new_state.value}")

    def track_api_call(self) -> None:
        """Track an API call for rate limiting."""
        self.api_calls_count += 1

    def get_state_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent state change history."""
        return self.state_history[-limit:]

    def get_stats(self) -> Dict[str, Any]:
        """Get Perception agent statistics."""
        base_stats = super().get_stats()

        # Calculate time in each state
        time_since_last_change = (datetime.utcnow() - self.last_activity).total_seconds()

        base_stats.update({
            'current_state': self.current_state.value,
            'total_state_changes': self.total_state_changes,
            'total_notifications_sent': self.total_notifications_sent,
            'total_resource_warnings': self.total_resource_warnings,
            'api_calls_count': self.api_calls_count,
            'api_calls_remaining': self.api_calls_limit - self.api_calls_count,
            'time_since_last_activity': time_since_last_change
        })
        return base_stats
