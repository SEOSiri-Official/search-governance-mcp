# tests/test_search_governance.py
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main_server import (
    audit_ai_crawler_directives,
    verify_canonical_link_integrity,
    enforce_brand_safety_guardrails,
    audit_xml_sitemap_index,
    notify_indexnow_search_engines,
    check_http_redirect_chain,
    validate_google_bot_user_agent,
    sanitize_governance_payload,
    get_live_governance_throughput_metrics,
    get_governance_server_specifications
)


def test_1_ai_crawler_directives():
    res = json.loads(audit_ai_crawler_directives("seosiri.com"))
    assert "status" in res


def test_2_canonical_integrity():
    res = json.loads(verify_canonical_link_integrity("https://seosiri.com"))
    assert "status" in res


def test_3_brand_safety():
    res = json.loads(enforce_brand_safety_guardrails("High quality technical SEO guide."))
    assert res["status"] == "SAFE"


def test_4_sitemap_audit():
    res = json.loads(audit_xml_sitemap_index("seosiri.com"))
    assert "status" in res


def test_5_indexnow_notifier():
    res = json.loads(notify_indexnow_search_engines("seosiri.com", "https://seosiri.com/page1.html"))
    assert res["status"] == "PAYLOAD_GENERATED"


def test_6_redirect_chain():
    res = json.loads(check_http_redirect_chain("https://seosiri.com"))
    assert res["status"] == "SUCCESS"


def test_7_googlebot_user_agent():
    res = json.loads(validate_google_bot_user_agent("https://seosiri.com"))
    assert "status" in res


def test_8_sanitize_payload():
    res = json.loads(sanitize_governance_payload("text <script>alert('xss')</script>"))
    assert res["status"] == "SANITIZED"


def test_9_throughput_metrics():
    res = json.loads(get_live_governance_throughput_metrics())
    assert res["status"] == "HEALTHY"


def test_10_server_specs():
    res = json.loads(get_governance_server_specifications())
    assert res["total_tools"] == 10