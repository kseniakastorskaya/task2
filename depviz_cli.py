import argparse
import gzip
import sys
from urllib.parse import urlparse
import urllib.request
import os


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
        with urllib.request.urlopen(repo_url) as response:
            bytearray = response.read()
            bytearray = gzip.decompress(bytearray)
            content = bytearray.decode('utf-8')
    except Exception as e:
        print(f"Ошибка при загрузке репозитория: {e}")
        sys.exit(1)

    current_package = None
    current_version = None
    in_target_package = False
    dependencies = []
    packages_found = []
    found_exact_match = False
    use_version = version

    for line in content.splitlines():
        if line.startswith("Package: "):
            current_package = line.split("Package: ")[1].strip()
            in_target_package = (current_package == package_name)

        elif line.startswith("Version: ") and in_target_package:
            current_version = line.split("Version: ")[1].strip()
            packages_found.append(current_version)

            if current_version == version:
                found_exact_match = True
                use_version = current_version
                print(f"✓ Найдено точное совпадение версии: {version}")

    if not found_exact_match and packages_found:
        use_version = packages_found[0]
        print(f"Точное совпадение версии '{version}' не найдено.")
        print(f"Доступные версии пакета {package_name}:")
        for ver in packages_found:
            print(f"  - {ver}")
        print(f"Используем версию: {use_version}")
    elif not packages_found:
        print(f"Пакет {package_name} не найден в репозитории")
        return []

    current_package = None
    current_version = None
    in_target_package = False
    dependencies = []

    for line in content.splitlines():
        if line.startswith("Package: "):
            current_package = line.split("Package: ")[1].strip()
            in_target_package = (current_package == package_name)

        elif line.startswith("Version: ") and in_target_package:
            current_version = line.split("Version: ")[1].strip()

        elif line.startswith("Depends: ") and in_target_package and current_version == use_version:
            deps_line = line.split("Depends: ")[1].strip()
            dependencies.extend([dep.strip() for dep in deps_line.split(",")])

        elif in_target_package and current_version == use_version and line.startswith(" ") and dependencies:
            continuation_line = line.strip()
            if continuation_line:
                dependencies = deps_line.split(",")

        elif line == "" and in_target_package and current_version == use_version and dependencies:
            break

    cleaned_dependencies = []
    for dep in dependencies:
        dep = dep.split(' (')[0].strip()
        dep = dep.split(' |')[0].strip()
        if dep and dep not in cleaned_dependencies:
            cleaned_dependencies.append(dep)

    return cleaned_dependencies


def main():
    parser = argparse.ArgumentParser(description="CLI для визуализации зависимостей пакета")

    parser.add_argument("--package", required=True, help="Имя пакета")
    parser.add_argument("--repo", required=True, help="URL репозитория или путь к локальному репозиторию")
    parser.add_argument("--version", required=True, help="Версия пакета")
    parser.add_argument("--mode", choices=["local", "remote"], default="remote",
                        help="Режим работы: local (локально) или remote (удалённый)")
    parser.add_argument("--max-depth", type=int, default=3,
                        help="Максимальная глубина анализа (по умолчанию 3)")

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

        if args.mode == "remote":
            dependencies = get_ubuntu_dependencies(args.package, args.version, repo)
            print("\nPlantUML граф зависимостей:")
            print("@startuml")
            if dependencies:
                for dep in dependencies:
                    print(f'"{args.package}" --> "{dep}"')
            else:
                print(f'"{args.package}" --> "Нет зависимостей"')
            print("@enduml")
        else:
            print("Локальный режим пока не поддерживает сбор зависимостей (только remote).")

    except ValueError as e:
        print(f"Ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()