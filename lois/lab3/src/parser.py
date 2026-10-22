#########################################################################################################################################
# Индивидуальная практическая работа 1 по дисциплине ЛОИС
# Выполнена студентами группы 421702 БГУИР Шумиловым Артемом Андреевичем, Пушистовой Екатериной Сергеевной, Ященко Александрой Вадимовной
# Модуль синтаксического анализа базы знаний по БНФ-грамматике
# Версия 1.1 от 16.10.2024
#
# Практикум по логическим основам интеллектуальных систем / В. В. Голенков и др. — Минск: БГУИР, 2011.
##########################################################################################################################################

import re
import sys
from .models import FuzzyRule, FuzzySet


class KnowledgeBaseParser:
    """Синтаксический анализатор базы знаний со строгим контролем БНФ (без пробелов)."""

    @staticmethod
    def parse_file(filepath: str) -> tuple[list[FuzzySet], list[FuzzyRule]]:
        facts: list[FuzzySet] = []
        rules: list[FuzzyRule] = []

        # Словарь для проверки уникальности имен предикатов: pred_name -> FuzzySet
        declared_predicates: dict[str, FuzzySet] = {}

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"[Ошибка открытия файла]: {e}")
            sys.exit(1)

        raw_lines = content.splitlines()
        is_rules_section = False

        for line_num, raw_line in enumerate(raw_lines, start=1):
            # Удаляем только символы переноса строки (но не пробелы!)
            line = raw_line.rstrip("\r\n")

            if not line:
                continue

            # Проверка: пробелы и табуляции строго запрещены грамматикой БЗ
            if " " in line or "\t" in line:
                raise ValueError(
                    f"Строка {line_num}: Обнаружен запрещённый символ: '{line}'. "
                    f"По БНФ-грамматике пробелы в базе знаний строго запрещены!"
                )

            if "~>" in line:
                is_rules_section = True
                rules.append(KnowledgeBaseParser._parse_rule(line, line_num))
            else:
                if is_rules_section:
                    raise ValueError(
                        f"Строка {line_num}: Нарушение БНФ — факты не могут следовать после правил."
                    )
                fact = KnowledgeBaseParser._parse_fact(line, line_num)

                # Семантическая проверка уникальности предикатов
                if fact.pred_name in declared_predicates:
                    prev = declared_predicates[fact.pred_name]
                    raise ValueError(
                        f"Семантическая ошибка в строке {line_num}: предикат '{fact.pred_name}' "
                        f"уже был объявлен ранее как '{prev.full_predicate_name}'. "
                        f"Повторное определение предиката недопустимо!"
                    )

                declared_predicates[fact.pred_name] = fact
                facts.append(fact)

        if not facts:
            raise ValueError("База знаний пуста или не содержит фактов.")
        return facts, rules

    @staticmethod
    def _parse_fact(line: str, line_num: int) -> FuzzySet:
        if "=" not in line:
            raise ValueError(f"Строка {line_num}: Отсутствует символ '=': '{line}'")

        if line.count("=") != 1:
            raise ValueError(f"Строка {line_num}: Строка факта должна содержать ровно один символ '=': '{line}'")

        left, right = line.split("=", 1)
        pred_name, var_name = KnowledgeBaseParser._parse_predicate_header(left, line_num)

        if not (right.startswith("{") and right.endswith("}")):
            raise ValueError(
                f"Строка {line_num}: Множество должно быть заключено в '{{}}': '{right}'"
            )

        inner = right[1:-1]
        if not inner:
            raise ValueError(f"Строка {line_num}: Нечёткое множество не может быть пустым.")

        # Строгая БНФ-проверка списка пар: <элемент,степень>,<элемент,степень>...
        pair_re = r"<[a-zA-Z][a-zA-Z0-9]*,(?:0(?:\.\d+)?|1(?:\.0+)?)>"
        set_re = rf"^{pair_re}(?:,{pair_re})*$"

        if not re.match(set_re, inner):
            raise ValueError(
                f"Строка {line_num}: Некорректный синтаксис нечёткого множества: '{right}'. "
                f"Ожидается формат: {{<элемент,степень>,...}} строго без пробелов и посторонних символов."
            )

        elements: dict[str, float] = {}
        pairs = re.findall(r"<([^<>]+)>", inner)
        for p in pairs:
            elem, deg_str = p.split(",")

            if elem in elements:
                raise ValueError(
                    f"Строка {line_num}: Дублирование элемента '{elem}' в нечётком множестве: '{right}'"
                )

            elements[elem] = float(deg_str)

        return FuzzySet(pred_name, var_name, elements)

    @staticmethod
    def _parse_rule(line: str, line_num: int) -> FuzzyRule:
        if line.count("~>") != 1:
            raise ValueError(f"Строка {line_num}: Ожидается ровно один оператор '~>': '{line}'")

        parts = line.split("~>")
        ant_pred, ant_var = KnowledgeBaseParser._parse_predicate_header(parts[0], line_num)
        cons_pred, cons_var = KnowledgeBaseParser._parse_predicate_header(parts[1], line_num)

        return FuzzyRule(ant_pred, ant_var, cons_pred, cons_var)

    @staticmethod
    def _parse_predicate_header(pred_str: str, line_num: int) -> tuple[str, str]:
        m = re.match(r"^([a-zA-Z][a-zA-Z0-9]*)\(([a-zA-Z][a-zA-Z0-9]*)\)$", pred_str)
        if not m:
            raise ValueError(
                f"Строка {line_num}: Некорректное имя предиката '{pred_str}'. Формат: Predicate(x) без пробелов."
            )
        return m.group(1), m.group(2)