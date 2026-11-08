import logging
import sys


def setup_logging(debug: bool) -> None:
    """配置全局日志格式与级别。"""
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        stream=sys.stdout,
        force=True,
    )
