# seosiri-search-governance-mcp

> 📖 **Official Architecture & Documentation:** [SEOSiri Search Governance Guide](https://www.seosiri.com/2026/08/search-governance-mcp.html) | [Central MCP Directory](https://www.seosiri.com/2026/07/seosiri-mcp-servers.html)

An open-source, local-first Model Context Protocol (MCP) server for **AI Search Crawler Governance, Brand Safety Guardrails, Canonical Integrity, and IndexNow Notifications**.

## 💖 Sponsorship, B2B Custom Solutions & Attribution

### 👨‍💻 Lead Architect & Attribution
Designed and engineered by **[Momenul Ahmad](https://github.com/MOBILEPHONE)**, Lead Architect and Founder of **[SEOSiri](https://seosiri.com)**.

### 🚀 Capabilities & Tools (10 Production Tools)
- **`audit_ai_crawler_directives`**: Parses `robots.txt` for AI search bot access rules (GPTBot, ClaudeBot, PerplexityBot).
- **`verify_canonical_link_integrity`**: Audits HTML `<link rel="canonical">` self-referential integrity.
- **`enforce_brand_safety_guardrails`**: Scans content strings for restricted keywords or unverified claims.
- **`audit_xml_sitemap_index`**: Validates XML sitemaps for syntax errors and URL counts.
- **`notify_indexnow_search_engines`**: Generates IndexNow API payloads for Bing, Yandex, and Naver.
- **`check_http_redirect_chain`**: Traces HTTP redirect loops ($301\text{/}\text{302}$).
- **`validate_google_bot_user_agent`**: Simulates Googlebot and ClaudeBot requests.
- **`sanitize_governance_payload`**: Strips script injections and malicious tags.
- **`get_live_governance_throughput_metrics`**: Monitors system health and processing latency.
- **`get_governance_server_specifications`**: Returns protocol specs and capability matrices.

## Quickstart

```bash
pip install -e .
pytest tests/test_search_governance.py
```

### 🔌 Claude Desktop / Cursor Configuration

Add this block to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "seosiri-search-governance": {
      "command": "uv",
      "args": [
        "run",
        "--github",
        "SEOSiri-Official/search-governance-mcp",
        "src/main_server.py"
      ]
    }
  }
}
```

## License

Distributed under the [MIT License](https://github.com/SEOSiri-Official/search-governance-mcp/blob/main/LICENSE).
