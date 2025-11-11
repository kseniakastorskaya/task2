import argparse
import os
import sys
from urllib.parse import urlparse
import urllib.request

def validate_url(url):
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError(f"Некорректный URL: {url}")
    return url

def validate_path(path):
    if not os.path.exists(path):
        raise ValueError(f"Указанный путь не существует: {path}")
    return path

def get_ubuntu_dependencies(package_name, version, repo_url):
    try:
        print(f"Загружаем данные пакета с {repo_url} ...")
        with urllib.request.urlopen(repo_url) as response:
            content = response.read().decode('utf-8')
    except Exception as e:
        print(f"Ошибка при загрузке репозитория: {e}")
        sys.exit(1)

    dependencies = None
    current_package = None
    current_version = None

    for line in content.splitlines():
        if line.startswith("Package: "):
            current_package = line.split("Package: ")[1].strip()
        elif line.startswith("Version: "):
            current_version = line.split("Version: ")[1].strip()
        elif line.startswith("Depends: ") and current_package == package_name and current_version == version:
            deps_line = line.split("Depends: ")[1].strip()
            dependencies = [dep.split(" ")[0].split("|")[0].strip() for dep in deps_line.split(",")]
            break

    if dependencies is None:
        print(f"Пакет {package_name} версии {version} не найден или у него нет прямых зависимостей")
        return []

    return dependencies

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

        # Этап 2 — сбор данных о прямых зависимостях
        if args.mode == "remote":
            dependencies = get_ubuntu_dependencies(args.package, args.version, repo)
            print("\nПрямые зависимости пакета:")
            if dependencies:
                for dep in dependencies:
                    print(f"- {dep}")
            else:
                print("Нет прямых зависимостей или пакет не найден.")

        else:
            print("Локальный режим пока не поддерживает сбор зависимостей (только remote).")

    except ValueError as e:
        print(f"Ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
