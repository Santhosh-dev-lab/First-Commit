from typing import Any
from domains.edge.gateway import EdgeGateway
from app.simulation.virtual_farm.gateway import VirtualEdgeGateway
from infrastructure.edge.aws_iot_gateway import AwsIoTGateway

class GatewayFactory:
    @staticmethod
    def create_gateway(farm_id: str, connection_mode: str, config: dict[str, Any] | None = None) -> EdgeGateway:
        if config is None:
            config = {}
            
        if connection_mode == "LOCAL_SIMULATION":
            # For Virtual Farm, we need a way to get the *same* instance of the gateway
            # so the runtime can poll it for commands.
            from app.api.routes.virtual_farm import _active_runtimes
            if farm_id in _active_runtimes:
                return _active_runtimes[farm_id].gateway
            # Fallback
            gw = VirtualEdgeGateway(farm_id=farm_id, client_id=f"sim-{farm_id}")
            gw.connect()
            return gw
        elif connection_mode == "AWS":
            endpoint = config.get("aws_endpoint", "mock-endpoint.iot.us-east-1.amazonaws.com")
            client_id = config.get("aws_client_id", f"gw-{farm_id}")
            gw = AwsIoTGateway(endpoint=endpoint, client_id=client_id, farm_id=farm_id)
            gw.connect()
            return gw
        elif connection_mode == "LOCAL_EDGE":
            gw = VirtualEdgeGateway(farm_id=farm_id, client_id=f"local-{farm_id}")
            gw.connect()
            return gw
        else:
            raise ValueError(f"Unknown connection mode: {connection_mode}")

gateway_factory = GatewayFactory()
