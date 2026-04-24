def test_dample():
    """
    A simple test to demonstrate basic assertion functionality.
    """
    assert 1 + 1 == 2, "Basic addition should work"


def test_service_api_response_parse_empty_body_204():
    """DELETE 等端點常回 204 無 body；parse 不可呼叫 .json() 拋錯。"""
    import httpx

    from src.infra.template.service_response import ServiceApiResponse

    resp = httpx.Response(204, content=b"")
    parsed = ServiceApiResponse.parse(resp)
    assert parsed.status_code == 204
    assert parsed.data is None
    assert parsed.res_json == {}