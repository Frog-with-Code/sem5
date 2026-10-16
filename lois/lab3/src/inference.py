########################################################################################
# Индивидуальная практическая работа 1 по дисциплине ЛОИС
# Выполнена студентами группы 421702 БГУИР Шумиловым Артемом Андреевичем, Пушистовой Екатериной Сергеевной, Ященко Александрой Вадимовной
# Модуль алгоритма прямого нечёткого логического вывода (Generalized Modus Ponens)
# Версия 1.0 от 16.10.2024
#
# Ссылки на материалы:
# Практикум по логическим основам интеллектуальных систем / В. В. Голенков и др. — Минск: БГУИР, 2011.
########################################################################################

from .models import FuzzyRule, FuzzySet
from .operations import godel_implication, t_norm_min


class DirectFuzzyInferenceEngine:
    """Движок выполнения прямого нечёткого логического вывода."""

    def __init__(self, facts: list[FuzzySet], rules: list[FuzzyRule]):
        self.known_facts: list[FuzzySet] = list(facts)
        self.rules: list[FuzzyRule] = rules
        self.derived_facts: list[FuzzySet] = []
        self._derived_counter: int = 1

    def compute_all_rule_implications(self):
        """Шаг 2: Вычисление отношений нечёткой импликации Гёделя для всех правил."""
        print("\n" + "=" * 65)
        print(" ШАГ 2: ВЫЧИСЛЕНИЕ НЕЧЁТКИХ ИМПЛИКАЦИЙ ДЛЯ КАЖДОГО ПРАВИЛА")
        print("=" * 65)

        for rule in self.rules:
            ant_fact = self._find_base_fact(rule.ant_pred, rule.ant_var)
            cons_fact = self._find_base_fact(rule.cons_pred, rule.cons_var)

            if not ant_fact or not cons_fact:
                print(
                    f"[!] Предупреждение: для правила {rule} "
                    f"не найдены базовые факты посылки или заключения."
                )
                continue

            print(f"\nПравило:    {rule}")
            print(f"Посылка:    {ant_fact}")
            print(f"Заключение: {cons_fact}")
            print("\nМатрица отношения импликации Гёделя R(x, y):")

            x_keys = list(ant_fact.elements.keys())
            y_keys = list(cons_fact.elements.keys())

            col_header = "       " + " ".join([f"{y:>8}" for y in y_keys])
            print(col_header)
            print("-" * len(col_header))

            for x in x_keys:
                row_str = f"{x:>5} |"
                for y in y_keys:
                    val = godel_implication(ant_fact.elements[x], cons_fact.elements[y])
                    rule.relation_matrix[(x, y)] = val
                    row_str += f"{val:8.4f}"
                print(row_str)

    def run_inference(self):
        """Шаг 3: Итеративный процесс прямого нечёткого вывода."""
        print("\n" + "=" * 65)
        print(" ШАГ 3: ПРОЦЕСС ПРЯМОГО НЕЧЁТКОГО ЛОГИЧЕСКОГО ВЫВОДА")
        print("=" * 65)

        iteration = 1
        while True:
            print(f"\n--- Итерация прямого вывода №{iteration} ---")
            new_facts_in_iteration: list[FuzzySet] = []

            for rule in self.rules:
                if not rule.relation_matrix:
                    continue

                for fact in list(self.known_facts):
                    # Факт может быть применен к правилу, если совпадают переменные носителя
                    if fact.var_name != rule.ant_var:
                        continue

                    new_fact = self._apply_rule(fact, rule)
                    if new_fact and not self._is_already_known(new_fact):
                        new_facts_in_iteration.append(new_fact)
                        self.known_facts.append(new_fact)
                        self.derived_facts.append(new_fact)

                        print(f"[+] ВЫВЕДЕН НОВЫЙ ФАКТ!")
                        print(f"    Правило:   {rule}")
                        print(f"    Посылка:   {fact}")
                        print(f"    Результат: {new_fact}\n")

            if not new_facts_in_iteration:
                print(
                    "[*] Достигнута точка останова: новых фактов не выведено (множество фактов замкнуто)."
                )
                break

            # Прерывание по требованию пользователя
            cmd = (
                input(
                    "Нажмите Enter для продолжения или введите 'q'/'stop' для прерывания: "
                )
                .strip()
                .lower()
            )
            if cmd in ("q", "quit", "stop", "exit"):
                print("[!] Процесс прямого логического вывода прерван пользователем.")
                break

            iteration += 1

    def _apply_rule(self, fact_a_prime: FuzzySet, rule: FuzzyRule) -> FuzzySet | None:
        """
        Применение формулы Generalized Modus Ponens:
        B'(y) = sup_x min(A'(x), R(x, y))
        """
        y_elements = sorted(list({y for (_, y) in rule.relation_matrix.keys()}))
        x_elements = fact_a_prime.elements.keys()

        b_prime_dict: dict[str, float] = {}

        for y in y_elements:
            max_val = 0.0
            for x in x_elements:
                if (x, y) in rule.relation_matrix:
                    r_val = rule.relation_matrix[(x, y)]
                    a_val = fact_a_prime.elements[x]
                    conj_val = t_norm_min(a_val, r_val)
                    if conj_val > max_val:
                        max_val = conj_val
            b_prime_dict[y] = round(max_val, 4)

        derived_name = f"{rule.cons_pred}Der{self._derived_counter}"
        self._derived_counter += 1
        return FuzzySet(derived_name, rule.cons_var, b_prime_dict, is_derived=True)

    def _is_already_known(self, candidate: FuzzySet) -> bool:
        """Использует перегруженный __eq__ для проверки эквивалентности."""
        for f in self.known_facts:
            if f.var_name == candidate.var_name and f == candidate:
                return True
        return False

    def _find_base_fact(self, pred_name: str, var_name: str) -> FuzzySet | None:
        for f in self.known_facts:
            if f.pred_name == pred_name and f.var_name == var_name:
                return f
        return None

    def print_final_results(self):
        """Шаг 4: Вывод всех выведенных фактов в стандартный вывод."""
        print("\n" + "=" * 65)
        print(" ШАГ 4: ВСЕ ВЫВЕДЕННЫЕ ФАКТЫ (СТАНДАРТНЫЙ ВЫВОД В БНФ)")
        print("=" * 65)
        if not self.derived_facts:
            print("Новых фактов выведено не было.")
        else:
            for idx, fact in enumerate(self.derived_facts, start=1):
                print(f"{idx}) {fact}")
        print("=" * 65 + "\n")