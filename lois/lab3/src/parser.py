#########################################################################################################################################
# Индивидуальная практическая работа 1 по дисциплине ЛОИС
# Выполнена студентами группы 421702 БГУИР Шумиловым Артемом Андреевичем, Пушистовой Екатериной Сергеевной, Ященко Александрой Вадимовной
# Модуль синтаксического анализа базы знаний по БНФ-грамматике
# Версия 1.0 от 16.10.2024
#
# Практикум по логическим основам интеллектуальных систем / В. В. Голенков и др. — Минск: БГУИР, 2011.
##########################################################################################################################################

import re
import sys
from .models import FuzzyRule, FuzzySet


class KnowledgeBaseParser:
    """Синтаксический анализатор базы знаний."""

    IDENT_RE = r"^[a-zA-Z][a-zA-Z0-9]*$"
    DEGREE_RE = r"^(0(\.\d+)?|1(\.0+)?)$"

    @staticmethod
    def parse_file(filepath: str) -> tuple[list[FuzzySet], list[FuzzyRule]]:
        facts: list[FuzzySet] = []
        rules: list[FuzzyRule] = []

        # Словарь для проверки уникальности имен предикатов: pred_name -> FuzzySet
        declared_predicates: dict[str, FuzzySet] = {}

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]
        except Exception as e:
            print(f"[Ошибка открытия файла]: {e}")
            sys.exit(1)

        is_rules_section = False
        for line_num, line in enumerate(lines, start=1):
            if "~>" in line:
                is_rules_section = True
                rules.append(KnowledgeBaseParser._parse_rule(line, line_num))
            else:
                if is_rules_section:
                    raise ValueError(
                        f"Строка {line_num}: Нарушение БНФ — факты не могут следовать после правил."
                    )
                fact = KnowledgeBaseParser._parse_fact(line, line_num)

                # Семантическая проверка, встречался ли предикат с таким именем
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
            raise ValueError(f"Строка {line_num}: Отсутствует символ '=': {line}")

        left, right = line.split("=", 1)
        pred_name, var_name = KnowledgeBaseParser._parse_predicate_header(
            left.strip(), line_num
        )

        right = right.strip()
        if not (right.startswith("{") and right.endswith("}")):
            raise ValueError(
                f"Строка {line_num}: Множество должно быть заключено в '{{}}': {right}"
            )

        inner = right[1:-1].strip()
        if not inner:
            raise ValueError(f"Строка {line_num}: Нечёткое множество не может быть пустым.")

        elements: dict[str, float] = {}
        pairs = re.findall(r"<([^<>]+)>", inner)
        if not pairs:
            raise ValueError(
                f"Строка {line_num}: Отсутствуют корректные пары <элемент,степень>."
            )

        for p in pairs:
            parts = p.split(",")
            if len(parts) != 2:
                raise ValueError(
                    f"Строка {line_num}: Пара '{p}' должна содержать ровно два значения через запятую."
                )

            elem = parts[0].strip()
            deg_str = parts[1].strip()

            if not re.match(KnowledgeBaseParser.IDENT_RE, elem):
                raise ValueError(
                    f"Строка {line_num}: Некорректный идентификатор элемента '{elem}'."
                )
            if not re.match(KnowledgeBaseParser.DEGREE_RE, deg_str):
                raise ValueError(
                    f"Строка {line_num}: Степень принадлежности '{deg_str}' вне диапазона [0; 1]."
                )

            elements[elem] = float(deg_str)

        return FuzzySet(pred_name, var_name, elements)

    @staticmethod
    def _parse_rule(line: str, line_num: int) -> FuzzyRule:
        parts = line.split("~>")
        if len(parts) != 2:
            raise ValueError(f"Строка {line_num}: Ожидается один оператор '~>': {line}")

        ant_pred, ant_var = KnowledgeBaseParser._parse_predicate_header(
            parts[0].strip(), line_num
        )
        cons_pred, cons_var = KnowledgeBaseParser._parse_predicate_header(
            parts[1].strip(), line_num
        )
        return FuzzyRule(ant_pred, ant_var, cons_pred, cons_var)

    @staticmethod
    def _parse_predicate_header(pred_str: str, line_num: int) -> tuple[str, str]:
        m = re.match(r"^([a-zA-Z][a-zA-Z0-9]*)\(([a-zA-Z][a-zA-Z0-9]*)\)$", pred_str)
        if not m:
            raise ValueError(
                f"Строка {line_num}: Некорректное имя предиката '{pred_str}'. Формат: Predicate(x)."
            )
        return m.group(1), m.group(2)