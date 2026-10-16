########################################################################################
# Индивидуальная практическая работа 1 по дисциплине ЛОИС
# Выполнена студентами группы 421702 БГУИР Шумиловым Артемом Андреевичем, Пушистовой Екатериной Сергеевной, Ященко Александрой Вадимовной
# Модуль структур данных: представление нечётких предикатов (множеств) и правил
# Версия 1.0 от 16.10.2024
#
# Ссылки на материалы:
# Практикум по логическим основам интеллектуальных систем / В. В. Голенков и др. — Минск: БГУИР, 2011.
#########################################################################################


class FuzzySet:
    """Структура данных для хранения нечёткого предиката: Name(var) = {<elem, degree>, ...}."""

    def __init__(
        self,
        pred_name: str,
        var_name: str,
        elements: dict[str, float],
        is_derived: bool = False,
    ):
        self.pred_name: str = pred_name
        self.var_name: str = var_name
        self.elements: dict[str, float] = (
            elements  # имя_элемента -> степень_принадлежности
        )
        self.is_derived: bool = is_derived

    @property
    def full_predicate_name(self) -> str:
        """Возвращает сигнатуру предиката: например, A(x)."""
        return f"{self.pred_name}({self.var_name})"

    def __str__(self) -> str:
        """Форматирует нечёткий факт в строгое соответствие с БНФ-грамматикой."""
        pairs = []
        for elem, deg in self.elements.items():
            deg_str = f"{deg:.4f}".rstrip("0").rstrip(".")
            if deg_str == "":
                deg_str = "0"
            if "." not in deg_str and deg_str != "1" and deg_str != "0":
                deg_str = f"{deg:.1f}"
            pairs.append(f"<{elem},{deg_str}>")
        return f"{self.pred_name}({self.var_name})={{{','.join(pairs)}}}"

    def __eq__(self, other: object, tol: float = 1e-4) -> bool:
        if not isinstance(other, FuzzySet):
            return False
        if self.elements.keys() != other.elements.keys():
            return False
        for k in self.elements:
            if abs(self.elements[k] - other.elements[k]) > tol:
                return False
        return True

    def __repr__(self) -> str:
        return str(self)


class FuzzyRule:
    """Структура данных для хранения правила вида Antecedent(x) ~> Consequent(y)."""

    def __init__(self, ant_pred: str, ant_var: str, cons_pred: str, cons_var: str):
        self.ant_pred: str = ant_pred
        self.ant_var: str = ant_var
        self.cons_pred: str = cons_pred
        self.cons_var: str = cons_var
        # Матрица нечёткого отношения импликации: (x_elem, y_elem) -> degree
        self.relation_matrix: dict[tuple[str, str], float] = {}

    def __str__(self) -> str:
        """Возвращает строковое представление правила."""
        return f"{self.ant_pred}({self.ant_var})~>{self.cons_pred}({self.cons_var})"
