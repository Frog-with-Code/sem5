#########################################################################################################################################
# Индивидуальная практическая работа 1 по дисциплине ЛОИС
# Выполнена студентами группы 421702 БГУИР Шумиловым Артемом Андреевичем, Пушистовой Екатериной Сергеевной, Ященко Александрой Вадимовной
# Модуль алгоритма прямого нечёткого логического вывода (Generalized Modus Ponens)
# Версия 1.0 от 16.10.2024
#
# Практикум по логическим основам интеллектуальных систем / В. В. Голенков и др. — Минск: БГУИР, 2011.
#########################################################################################################################################

from .models import FuzzyRule, FuzzySet
from .operations import godel_implication, t_norm_min


class DirectFuzzyInferenceEngine:
    """Движок прямого нечёткого вывода с поддержкой унификации переменных и контролем понятий."""

    def __init__(self, facts: list[FuzzySet], rules: list[FuzzyRule]):
        self.known_facts: list[FuzzySet] = list(facts)
        self.rules: list[FuzzyRule] = rules
        self.derived_facts: list[FuzzySet] = []
        self._derived_counter: int = 1

    def compute_all_rule_implications(self):
        """Вычисление отношений нечёткой импликации Гёделя для всех правил."""

        print("\n" + "=" * 65)
        print(" ШАГ 2: ВЫЧИСЛЕНИЕ НЕЧЁТКИХ ИМПЛИКАЦИЙ ДЛЯ КАЖДОГО ПРАВИЛА")
        print("=" * 65)

        for rule in self.rules:
            # Базовые факты ищутся по имени понятия (предиката), переменные в скобках унифицируются
            ant_fact = self._find_base_fact_by_pred(rule.ant_pred)
            cons_fact = self._find_base_fact_by_pred(rule.cons_pred)

            if not ant_fact or not cons_fact:
                print(
                    f"[!] Предупреждение: для правила {rule} не найдены базовые факты "
                    f"для понятий '{rule.ant_pred}' или '{rule.cons_pred}'."
                )
                continue

            print(f"\nПравило:    {rule}")
            print(f"Посылка (факт {ant_fact.full_predicate_name}):    {ant_fact}")
            print(f"Заключение (факт {cons_fact.full_predicate_name}): {cons_fact}")
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
        """Итеративный процесс прямого логического вывода (Forward Chaining)."""

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
                    # Проверяем, подходит ли факт к посылке правила
                    if not self._can_unify(fact, rule):
                        continue

                    new_fact = self._apply_rule(fact, rule)
                    # Проверяем новизну факта именно для данного целевого понятия (консеквента)
                    if new_fact and not self._is_already_known(new_fact, rule):
                        new_facts_in_iteration.append(new_fact)
                        self.known_facts.append(new_fact)
                        self.derived_facts.append(new_fact)
                        self._derived_counter += 1

                        print(f"[+] ВЫВЕДЕН НОВЫЙ ФАКТ!")
                        print(f"    Правило:           {rule}")
                        print(f"    Использован факт:  {fact} (унифицирован с {rule.ant_pred}({rule.ant_var}))")
                        print(f"    Результат:         {new_fact}\n")

            if not new_facts_in_iteration:
                print(
                    "[*] Достигнута точка останова: новых фактов не выведено (множество знаний замкнуто)."
                )
                break

            # Возможность прерывания процесса вывода пользователем
            cmd = (
                input("Нажмите Enter для продолжения или введите 'q'/'stop' для завершения: ")
                .strip()
                .lower()
            )
            if cmd in ("q", "quit", "stop", "exit"):
                print("[!] Процесс прямого логического вывода прерван пользователем.")
                break

            iteration += 1

    def _can_unify(self, fact: FuzzySet, rule: FuzzyRule) -> bool:
        """
        Проверка применимости факта к правилу:
        1. Базовое понятие факта (base_pred) совпадает с предикатом посылки правила.
        2. Носитель элементов факта строго совпадает со строками матрицы правила
           (элементы — это предметные константы, они не унифицируются).
        """
        fact_base = getattr(fact, "base_pred", fact.pred_name)
        if fact_base != rule.ant_pred:
            return False

        # Элементы носителя факта обязаны совпадать с элементами строк отношения R(x, y)
        rule_x_elements = {x for (x, _) in rule.relation_matrix.keys()}
        fact_elements = set(fact.elements.keys())

        return fact_elements == rule_x_elements

    def _apply_rule(self, fact_a_prime: FuzzySet, rule: FuzzyRule) -> FuzzySet | None:
        """
        Применение обобщенного Модус Поненс (GMP):
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

        # Формируем имя выведенного факта и связываем его с базовым понятием заключения
        derived_name = f"{rule.cons_pred}Der{self._derived_counter}"

        return FuzzySet(
            pred_name=derived_name,
            var_name=rule.cons_var,
            elements=b_prime_dict,
            base_pred=rule.cons_pred,
            is_derived=True,
        )

    def _is_already_known(self, candidate: FuzzySet, rule: FuzzyRule) -> bool:
        """
        Проверяет, известно ли уже такое нечёткое множество для целевого понятия.
        Исключает ложное срабатывание между разными понятиями.
        """
        for f in self.known_facts:
            f_base = f.base_pred
            if f_base == rule.cons_pred and f.has_same_fuzzy_set(candidate):
                    return True
        return False

    def _find_base_fact_by_pred(self, pred_name: str) -> FuzzySet | None:
        """Поиск исходного факта по имени понятия."""

        for f in self.known_facts:
            f_base = getattr(f, "base_pred", f.pred_name)
            if not f.is_derived and f_base == pred_name:
                return f
        return None

    def print_final_results(self):
        """Вывод всех выведенных фактов в стандартный поток."""

        print("\n" + "=" * 65)
        print(" ШАГ 4: ВСЕ ВЫВЕДЕННЫЕ ФАКТЫ (СТАНДАРТНЫЙ ВЫВОД В БНФ)")
        print("=" * 65)
        if not self.derived_facts:
            print("Новых фактов выведено не было.")
        else:
            for idx, fact in enumerate(self.derived_facts, start=1):
                print(f"{idx}) {fact}")
        print("=" * 65 + "\n")