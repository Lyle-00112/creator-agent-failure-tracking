from creator_agent import process_content


class RecordingClient:
    def __init__(self):
        self.metrics = []
        self.errors = []

    def report(self, **payload):
        self.metrics.append(payload)

    def capture(self, **payload):
        self.errors.append(payload)


def test_delivery_failure_is_captured_and_not_marked_delivered():
    client = RecordingClient()
    result = process_content("asset-7", lambda _: "", client)
    assert result.delivered is False
    assert result.subscribers_updated == 0
    assert client.errors[0]["context"] == {"asset_id": "asset-7"}
    assert client.metrics == []
