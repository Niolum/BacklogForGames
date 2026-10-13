import argparse
import asyncio

from deps import init_deps
from domain.use_cases import import_catalog


def main(argv: list[str] | None = None) -> None:
    """Import games and their genres from RAWG. A positive limit is required."""
    limit = _limit(argv)
    init_deps()
    asyncio.run(import_catalog(limit))


def _limit(argv: list[str] | None) -> int:
    parser = argparse.ArgumentParser(description='Import games and their genres from RAWG.')
    parser.add_argument('--limit', required=True, type=_positive_int)
    args = parser.parse_args(argv)
    return args.limit


def _positive_int(value: str) -> int:
    limit = int(value)
    if limit < 1:
        msg = 'limit must be a positive integer'
        raise argparse.ArgumentTypeError(msg)
    return limit


if __name__ == '__main__':
    main()
