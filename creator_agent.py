import traceback
from dataclasses import dataclass
from typing import Callable

from infrai_client import InfraiClient

# The public idiom represented by this client is infrai.errors.capture.


@dataclass
class DeliveryResult:
    asset_id: str
    delivered: bool
    subscribers_updated: int


def process_content(asset_id: str, processor: Callable[[str], str], client: InfraiClient) -> DeliveryResult:
    """Process an asset, then deliver it and notify subscribers as one visible decision."""
    try:
        receipt = processor(asset_id)
        updated = publish_to_subscribers(asset_id, receipt)
        client.report(type="counter", name="creator.asset.processed", value=1, tags={"asset_id": asset_id})
        return DeliveryResult(asset_id, True, updated)
    except Exception as exc:
        client.capture(
            title="creator delivery failed",
            message=f"{type(exc).__name__}: {exc}",
            level="error",
            fingerprint=["creator-agent", "content-delivery"],
            exception=traceback.format_exc(),
            context={"asset_id": asset_id},
        )
        return DeliveryResult(asset_id, False, 0)


def publish_to_subscribers(asset_id: str, receipt: str) -> int:
    if not receipt:
        raise ValueError(f"empty delivery receipt for {asset_id}")
    return 1


if __name__ == "__main__":
    client = InfraiClient()
    result = process_content("asset-demo-001", lambda asset: f"receipt:{asset}", client)
    print(result)
