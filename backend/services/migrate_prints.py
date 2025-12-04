#!/usr/bin/env python3
"""Script para migrar print() para logging de forma segura."""
import re
import sys
from pathlib import Path


def migrate_prints_to_logging(filepath: Path) -> tuple[int, int]:
    """
    Migra todos os prints para logging.

    Returns:
        tuple: (prints_found, prints_migrated)
    """
    content = filepath.read_text()
    original_print_count = content.count('print(')

    # Padrões de substituição em ordem
    patterns = [
        # print("\n" + "=" * N) → logger.info("=" * N) for any N
        (r'print\("\\n" \+ "=" \* (\d+)\)', r'logger.info("=" * \1)'),

        # print("=" * N) → logger.info("=" * N) for any N
        (r'print\("=" \* (\d+)\)', r'logger.info("=" * \1)'),

        # print(f"text {var}") → logger.info("text %s", var)
        (r'print\(f"([^"]*?)\{([^}:]+?)\}([^"]*)"\)', r'logger.info("\1%s\3", \2)'),

        # print(f"text {var:.2f}") → logger.info("text %.2f", var)
        (r'print\(f"([^"]*?)\{([^}:]+?):(\.?\d*[fd])\}([^"]*)"\)', r'logger.info("\1%\3\4", \2)'),

        # print(f"text {var:.2%}") → logger.info("text %.2%%", var)
        (r'print\(f"([^"]*?)\{([^}:]+?):(\.?\d*%)\}([^"]*)"\)', r'logger.info("\1%\3\4", \2)'),

        # print("simple string") → logger.info("simple string")
        (r'print\("([^"]+)"\)', r'logger.info("\1")'),

        # print(f"text") sem variáveis → logger.info("text")
        (r'print\(f"([^{]*?)"\)', r'logger.info("\1")'),
    ]

    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)

    new_print_count = content.count('print(')
    migrated = original_print_count - new_print_count

    # Salva de volta
    filepath.write_text(content)

    return original_print_count, migrated


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python migrate_prints.py <file_path>")
        sys.exit(1)

    filepath = Path(sys.argv[1])

    if not filepath.exists():
        print(f"Error: File not found: {filepath}")
        sys.exit(1)

    found, migrated = migrate_prints_to_logging(filepath)
    remaining = found - migrated

    print(f"✅ Migration complete for {filepath.name}")
    print(f"   Prints found: {found}")
    print(f"   Prints migrated: {migrated}")
    print(f"   Prints remaining: {remaining}")

    if remaining > 0:
        print(f"\n⚠️  {remaining} prints could not be auto-migrated (complex patterns)")
