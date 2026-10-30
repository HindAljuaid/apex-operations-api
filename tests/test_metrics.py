def test_metrics_endpoint_returns_prometheus_format(client):
    response = client.get("/metrics")

    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    assert "apex_http_requests_total" in response.text


def test_metrics_records_api_requests(client):
    client.get("/health/live")

    response = client.get("/metrics")

    assert response.status_code == 200
    assert 'endpoint="/health/live"' in response.text
    assert "apex_http_request_duration_seconds_count" in response.text
