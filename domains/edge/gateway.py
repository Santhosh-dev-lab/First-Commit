from __future__ import annotations

import abc
from collections.abc import Callable

from domains.edge.models import CommandEnvelope, GatewayHeartbeat, TelemetryEnvelope


class EdgeGateway(abc.ABC):
    """
    Abstract interface for physical farm connectivity.
    
    This acts as the bridge between the PHYSICA domain logic and the real world
    (or local simulated world). It is transport-agnostic (MQTT, HTTP, local memory).
    """

    @abc.abstractmethod
    def connect(self) -> None:
        """Establish connection to the edge/broker."""

    @abc.abstractmethod
    def disconnect(self) -> None:
        """Close connection to the edge/broker."""

    @abc.abstractmethod
    def get_status(self) -> str:
        """Return the connection status (e.g., CONNECTED, DISCONNECTED)."""

    @abc.abstractmethod
    def publish_telemetry(self, telemetry: TelemetryEnvelope) -> None:
        """Publish a telemetry event from a device."""

    @abc.abstractmethod
    def publish_heartbeat(self, heartbeat: GatewayHeartbeat) -> None:
        """Publish a gateway heartbeat."""

    @abc.abstractmethod
    def send_command(self, command: CommandEnvelope) -> None:
        """Send a command to a device."""

    @abc.abstractmethod
    def set_telemetry_callback(self, callback: Callable[[TelemetryEnvelope], None]) -> None:
        """Register a callback to be invoked when telemetry is received from the edge."""

    @abc.abstractmethod
    def set_heartbeat_callback(self, callback: Callable[[GatewayHeartbeat], None]) -> None:
        """Register a callback to be invoked when a heartbeat is received."""
