########################################################################################
# Индивидуальная практическая работа 1 по дисциплине ЛОИС
# Выполнена студентами группы 421702 БГУИР Шумиловым Артемом Андреевичем, Пушистовой Екатериной Сергеевной, Ященко Александрой Вадимовной
# Главный файл программы (точка входа)
# Версия 1.0 от 16.10.2024
#
# Ссылки на материалы:
# Практикум по логическим основам интеллектуальных систем / В. В. Голенков и др. — Минск: БГУИР, 2011.
########################################################################################

from pathlib import Path

from .inference import DirectFuzzyInferenceEngine
from .parser import KnowledgeBaseParser


def resolve_kb_path(user_input: str) -> str:
    """
    Интеллектуальный поиск файла:
    1. Очищает от случайных кавычек при копировании пути.
    2. Проверяет путь относительно текущей папки терминала (CWD).
    3. Проверяет путь относительно директории скрипта main.py.
    4. Проверяет путь относительно корня проекта (родителя main.py).
    """
    clean_path = user_input.strip("\"' ")
    p = Path(clean_path)

    # 1. Если путь абсолютный или существует относительно текущей папки терминала
    if p.exists():
        return str(p.resolve())

    # 2. Относительно папки, где лежит сам main.py
    script_dir = Path(__file__).resolve().parent
    if (script_dir / clean_path).exists():
        return str((script_dir / clean_path).resolve())

    # 3. Относительно родительской папки (корня проекта)
    if (script_dir.parent / clean_path).exists():
        return str((script_dir.parent / clean_path).resolve())

    return clean_path


def main():
    print("=================================================================")
    print("  ЛОИС. Лабораторная работа №1. Прямой нечёткий вывод (Вар. 1)")
    print("=================================================================")

    filename = input("Введите имя файла базы знаний (по умолчанию 'kb.txt'): ").strip()
    if not filename:
        filename = "../kb/kb.txt"

    resolved_path = resolve_kb_path(filename)

    try:
        facts, rules = KnowledgeBaseParser.parse_file(resolved_path)
    except Exception as e:
        print(f"\n[Ошибка синтаксического анализа базы знаний]: {e}")
        return

    print(f"\n[Успешно загружено]: Фактов: {len(facts)}, Правил: {len(rules)}")

    engine = DirectFuzzyInferenceEngine(facts, rules)
    # Шаг 2
    engine.compute_all_rule_implications()
    # Шаг 3
    engine.run_inference()
    # Шаг 4
    engine.print_final_results()


if __name__ == "__main__":
    main()
