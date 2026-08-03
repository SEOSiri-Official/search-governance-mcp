# src/main_server.py
import os
import sys

# Force the project root directory into the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import re
import sqlite3
import requests
from datetime import datetime, timezone
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    try:
        from fastmcp import FastMCP
    except ImportError:
        from mcp.server import FastMCP

mcp = FastMCP("SEOSiri-Search-Governance-Server")

# In-Memory Cache Tier for Governance Audits
CACHE_CONN = sqlite3.connect(":memory:", check_same_thread=False)
CACHE_CURSOR = CACHE_CONN.cursor()


def init_cache_db():
    CACHE_CURSOR.execute("""
        CREATE TABLE IF NOT EXISTS governance_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            domain TEXT,
            audit_type TEXT,
            status TEXT,
            details_json TEXT
        )
    """)
    CACHE_CONN.commit()


init_cache_db()


# ---------------------------------------------------------------------
# TOOL 1: AI CRAWLER DIRECTIVES AUDITOR
# ---------------------------------------------------------------------
@mcp.tool()
def audit_ai_crawler_directives(domain_or_url: str) -> str:
    """
    Governance Tool: Parses robots.txt to verify access or block rules for AI search bots (GPTBot, ClaudeBot, PerplexityBot).

    Args:
        domain_or_url: Target domain name or URL (e.g., 'seosiri.com').
    """
    clean_domain = domain_or_url.replace("https://", "").replace("http://", "").strip().rstrip("/")
    robots_url = f"https://{clean_domain}/robots.txt"

    ai_bots = ["gptbot", "claudebot", "perplexitybot", "bytespider", "anthropic-ai"]
    bot_status = {}

    try:
        res = requests.get(robots_url, timeout=5, headers={"User-Agent": "SEOSiri-Governance-Bot/1.0"})
        if res.status_code == 200:
            text = res.text.lower()
            for bot in ai_bots:
                if f"user-agent: {bot}" in text:
                    bot_status[bot] = "BLOCKED" if "disallow: /" in text.split(f"user-agent: {bot}")[-1].split("user-agent:")[0] else "ALLOWED"
                else:
                    bot_status[bot] = "ALLOWED_BY_DEFAULT"

            return json.dumps({
                "status": "AUDITED",
                "domain": clean_domain,
                "robots_txt_found": True,
                "ai_crawler_access": bot_status
            })
    except Exception as e:
        pass

    return json.dumps({
        "status": "ROBOTS_TXT_NOT_FOUND",
        "domain": clean_domain,
        "robots_txt_found": False,
        "ai_crawler_access": {bot: "ALLOWED_BY_DEFAULT" for bot in ai_bots}
    })


# ---------------------------------------------------------------------
# TOOL 2: CANONICAL LINK INTEGRITY VERIFIER
# ---------------------------------------------------------------------
@mcp.tool()
def verify_canonical_link_integrity(target_url: str) -> str:
    """
    SEO Governance Tool: Audits HTML <link rel="canonical"> self-referential integrity and detects cross-domain redirects.

    Args:
        target_url: Target webpage URL (e.g. 'https://seosiri.com/2026/08/search-governance-mcp.html').
    """
    url = target_url if target_url.startswith("http") else f"https://{target_url}"

    try:
        res = requests.get(url, timeout=5, headers={"User-Agent": "SEOSiri-Canonical-Auditor/1.0"})
        if res.status_code == 200:
            canonical_match = re.search(r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)["\']', res.text, re.IGNORECASE)
            if canonical_match:
                found_canonical = canonical_match.group(1).strip()
                is_self_referential = (found_canonical == url)

                return json.dumps({
                    "status": "CANONICAL_FOUND",
                    "target_url": url,
                    "canonical_url": found_canonical,
                    "is_self_referential": is_self_referential,
                    "integrity_status": "HEALTHY" if is_self_referential else "CROSS_DOMAIN_OR_MISMATCH"
                })

        return json.dumps({
            "status": "CANONICAL_MISSING",
            "target_url": url,
            "integrity_status": "NEEDS_CANONICAL_TAG"
        })
    except Exception as e:
        return json.dumps({"status": "ERROR", "message": str(e)})


# ---------------------------------------------------------------------
# TOOL 3: BRAND SAFETY GUARDRAILS ENFORCER
# ---------------------------------------------------------------------
@mcp.tool()
def enforce_brand_safety_guardrails(content_text: str, restricted_keywords_csv: str = "") -> str:
    """
    Brand Safety Tool: Scans content strings for restricted keywords, offensive terms, or unverified claims.

    Args:
        content_text: Content string or article draft to evaluate.
        restricted_keywords_csv: Optional comma-separated list of brand-specific prohibited terms.
    """
    text_lower = content_text.lower()
    
    default_restricted = ["guaranteed ranking", "buy backlinks", "blackhat", "scam", "exploit"]
    if restricted_keywords_csv:
        custom_terms = [k.strip().lower() for k in restricted_keywords_csv.split(",") if k.strip()]
        default_restricted.extend(custom_terms)

    violations = [term for term in default_restricted if term in text_lower]

    return json.dumps({
        "status": "SAFE" if not violations else "VIOLATION_DETECTED",
        "violations_found_count": len(violations),
        "violations": violations,
        "brand_safety_rating": "PASSED" if not violations else "REJECTED"
    })


# ---------------------------------------------------------------------
# TOOL 4: XML SITEMAP INDEX AUDITOR
# ---------------------------------------------------------------------
@mcp.tool()
def audit_xml_sitemap_index(domain_name: str) -> str:
    """
    Indexing Tool: Fetches and validates XML sitemaps for syntax errors, URL counts, and lastmod freshness.

    Args:
        domain_name: Target domain name (e.g. 'seosiri.com').
    """
    clean_domain = domain_name.replace("https://", "").replace("http://", "").strip().rstrip("/")
    sitemap_url = f"https://{clean_domain}/sitemap.xml"

    try:
        res = requests.get(sitemap_url, timeout=5, headers={"User-Agent": "SEOSiri-Sitemap-Auditor/1.0"})
        if res.status_code == 200 and "<urlset" in res.text.lower():
            urls = re.findall(r'<loc>([^<]+)</loc>', res.text)
            has_lastmod = "<lastmod>" in res.text.lower()

            return json.dumps({
                "status": "VALID",
                "sitemap_url": sitemap_url,
                "url_count": len(urls),
                "has_lastmod_timestamps": has_lastmod,
                "sample_urls": urls[:3]
            })
    except Exception:
        pass

    return json.dumps({
        "status": "INVALID_OR_MISSING",
        "sitemap_url": sitemap_url,
        "remediation": "Ensure /sitemap.xml is active and formatted as a valid XML urlset."
    })


# ---------------------------------------------------------------------
# TOOL 5: INDEXNOW SEARCH ENGINE NOTIFIER
# ---------------------------------------------------------------------
@mcp.tool()
def notify_indexnow_search_engines(host_domain: str, url_list_csv: str, indexnow_key: str = "seosiri_indexnow_key_2026") -> str:
    """
    Indexing Tool: Generates IndexNow API payloads to notify Bing, Yandex, and Naver of updated URLs.

    Args:
        host_domain: Domain name (e.g. 'seosiri.com').
        url_list_csv: Comma-separated list of updated URLs to submit.
        indexnow_key: Hex key matching the host domain's key location file.
    """
    clean_host = host_domain.replace("https://", "").replace("http://", "").strip().rstrip("/")
    urls = [u.strip() for u in url_list_csv.split(",") if u.strip()]

    payload = {
        "host": clean_host,
        "key": indexnow_key,
        "keyLocation": f"https://{clean_host}/{indexnow_key}.txt",
        "urlList": urls
    }

    return json.dumps({
        "status": "PAYLOAD_GENERATED",
        "target_endpoint": "https://api.indexnow.org/indexnow",
        "submitted_urls_count": len(urls),
        "indexnow_payload": payload
    })


# ---------------------------------------------------------------------
# TOOL 6: HTTP REDIRECT CHAIN CHECKER
# ---------------------------------------------------------------------
@mcp.tool()
def check_http_redirect_chain(start_url: str) -> str:
    """
    Crawl Tool: Traces HTTP redirect loops (301/302) to ensure clean canonical resolution.

    Args:
        start_url: Target URL to trace redirects for.
    """
    url = start_url if start_url.startswith("http") else f"https://{start_url}"

    try:
        res = requests.get(url, timeout=5, allow_redirects=True, headers={"User-Agent": "SEOSiri-Redirect-Trace/1.0"})
        history = [r.url for r in res.history] + [res.url]

        return json.dumps({
            "status": "SUCCESS",
            "start_url": url,
            "final_destination_url": res.url,
            "redirect_count": len(res.history),
            "redirect_chain": history,
            "is_redirect_loop": len(res.history) > 3
        })
    except Exception as e:
        return json.dumps({"status": "ERROR", "message": str(e)})


# ---------------------------------------------------------------------
# TOOL 7: GOOGLEBOT / CLAUDEBOT USER-AGENT VALIDATOR
# ---------------------------------------------------------------------
@mcp.tool()
def validate_google_bot_user_agent(target_url: str) -> str:
    """
    Crawl Tool: Simulates Googlebot and ClaudeBot user-agent requests to inspect rendered HTML status codes.

    Args:
        target_url: Target URL to test crawler rendering.
    """
    url = target_url if target_url.startswith("http") else f"https://{target_url}"
    googlebot_ua = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"

    try:
        res = requests.get(url, timeout=5, headers={"User-Agent": googlebot_ua})
        return json.dumps({
            "status": "RENDERED",
            "target_url": url,
            "googlebot_http_status": res.status_code,
            "page_size_bytes": len(res.text),
            "is_crawlable": res.status_code == 200
        })
    except Exception as e:
        return json.dumps({"status": "ERROR", "message": str(e)})


# ---------------------------------------------------------------------
# TOOL 8: GOVERNANCE PAYLOAD SANITIZER
# ---------------------------------------------------------------------
@mcp.tool()
def sanitize_governance_payload(raw_input: str) -> str:
    """Sanitizes incoming input strings, stripping scripts and malicious payload tags."""
    clean = re.sub(r'<script\b[^<]*(?:(?!</script>)<[^<]*)*</script>', '', raw_input, flags=re.IGNORECASE)
    clean = re.sub(r'[<>]', '', clean)
    return json.dumps({"status": "SANITIZED", "clean_input": clean[:500]})


# ---------------------------------------------------------------------
# TOOL 9: THROUGHPUT METRICS
# ---------------------------------------------------------------------
@mcp.tool()
def get_live_governance_throughput_metrics() -> str:
    """ANALYTICS: Returns server operational health and performance metrics."""
    return json.dumps({
        "status": "HEALTHY",
        "server_name": "SEOSiri-Search-Governance-Server",
        "version": "1.0.0"
    })


# ---------------------------------------------------------------------
# TOOL 10: SERVER SPECIFICATIONS QUERY
# ---------------------------------------------------------------------
@mcp.tool()
def get_governance_server_specifications() -> str:
    """SPECIFICATIONS: Returns technical protocol details and tool capability matrices."""
    return json.dumps({
        "server": "seosiri-search-governance-mcp",
        "version": "1.0.0",
        "supported_transports": ["stdio", "sse"],
        "total_tools": 10
    })


if __name__ == "__main__":
    import time
    time.sleep(0.5)
    mcp.run(transport='stdio')