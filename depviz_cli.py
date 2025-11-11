import argparse
import os
import sys
from urllib.parse import urlparse


def validate_url(url):
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError(f"Некорректный URL: {url}")
    return url


def validate_path(path):
    if not os.path.exists(path):
        raise ValueError(f"Указанный путь не существует: {path}")
    return path


def main():
    parser = argparse.ArgumentParser(
        description="Прототип инструмента визуализации зависимостей пакета"
    )

    parser.add_argument("--package", required=True, help="Имя анализируемого пакета")
    parser.add_argument(
        "--repo", required=True,
        help="URL-адрес репозитория или путь к локальному тестовому репозиторию"
    )
    parser.add_argument(
        "--mode", choices=["local", "remote"], required=True,
        help="Режим работы: local (локальный путь) или remote (удалённый репозиторий)"
    )
    parser.add_argument("--version", required=True, help="Версия анализируемого пакета")
    parser.add_argument(
        "--max-depth", type=int, default=3,
        help="Максимальная глубина анализа зависимостей (по умолчанию 3)"
    )

    args = parser.parse_args()

    try:
        if args.mode == "remote":
            repo = validate_url(args.repo)
        else:
            repo = validate_path(args.repo)

        if args.max_depth <= 0:
            raise ValueError("Глубина анализа должна быть положительным числом")

        print("Настройки конфигурации:")
        print(f"Имя пакета = {args.package}")
        print(f"Репозиторий = {repo}")
        print(f"Режим работы = {args.mode}")
        print(f"Версия = {args.version}")
        print(f"Максимальная глубина = {args.max_depth}")

    except ValueError as e:
        print(f"Ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
