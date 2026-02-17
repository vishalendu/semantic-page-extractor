import argparse
import asyncio
import json

from semantic_page_extractor import extract_from_url


def _serialize(payload, minify: bool) -> str:
    if minify:
        return json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return json.dumps(payload, indent=2, sort_keys=True)


async def run(args: argparse.Namespace) -> None:
    result = await extract_from_url(
        args.url,
        wait_until=args.wait_until,
        actionable_only=args.actionable_only,
        intent=args.intent,
        min_score=args.min_score,
        max_results=args.max_results,
        output_format=args.output_format,
    )
    payload = result.model_dump(mode="json") if hasattr(result, "model_dump") else result
    print(_serialize(payload, args.minify))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract semantic page summary for a URL")
    parser.add_argument("url", help="Target URL to extract")
    parser.add_argument("--wait-until", default="load", choices=["load", "domcontentloaded", "networkidle", "commit"], help="Playwright wait condition for page.goto")
    parser.add_argument("--actionable-only", action="store_true", help="Print only deduplicated actionable elements")
    parser.add_argument("--intent", default=None, help="Filter actionable elements by intent query (e.g. 'add to cart')")
    parser.add_argument("--min-score", type=float, default=0.45, help="Minimum intent match score (0.0 to 1.0)")
    parser.add_argument("--max-results", type=int, default=None, help="Optional max number of filtered results")
    parser.add_argument("--minify", action="store_true", help="Print compact minified JSON output")
    parser.add_argument("--output-format", choices=["json", "compact"], default=None, help="Optional output format override: json strips action_signature/disabled, compact emits compressed payload")
    return parser.parse_args()


if __name__ == "__main__":
    asyncio.run(run(parse_args()))
