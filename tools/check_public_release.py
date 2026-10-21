"""Read-only deployment check; never prints cookies or authentication redirects."""
import json
from http.cookiejar import CookieJar
from urllib.request import build_opener, HTTPCookieProcessor


def main():
    opener = build_opener(HTTPCookieProcessor(CookieJar()))
    url = 'https://reacao-fischer-tropsch.streamlit.app/app/static/release.json'
    result = {'expected_version': '0.2.0', 'verified': False}
    try:
        with opener.open(url, timeout=30) as response:
            result['http_status'] = response.status
            content = response.read(65536)
        marker = json.loads(content)
        result['served_version'] = marker.get('version')
        result['verified'] = (
            marker.get('version') == '0.2.0'
            and marker.get('application') == 'Projeto Fischer–Tropsch'
            and marker.get('experimental_recommendations_validated') is False
        )
    except Exception as exc:
        result['error_type'] = type(exc).__name__
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result['verified'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
