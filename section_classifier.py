class SectionClassifier:
    def __init__(self, window_size=10):
        self.window_size = window_size
        self.label_int_history = [90] * window_size
        self.section_history = [0] * window_size

    def update_label_int(self, label_int):
        """
        Actualiza la historia de Label_int con el nuevo valor recibido.

        Args:
            label_int (int): El último Label_int recibido.
        """
        self.label_int_history.append(label_int)
        if len(self.label_int_history) > self.window_size:
            self.label_int_history.pop(0)

    def apply_heuristic_rules(self):
        """
        Aplica las reglas heurísticas para determinar la sección actual.

        Returns:
            int: La sección determinada según las reglas heurísticas.
        """
        current_label_int = self.label_int_history[-1]

        if current_label_int in [85, 83, 82, 25, 9]:
            new_section = (
                1
                if self.section_history.count(0) > len(self.section_history) / 2
                else self.section_history[-1]
            )
        elif current_label_int == 42:
            new_section = (
                2
                if self.section_history.count(1) > len(self.section_history) / 2
                else self.section_history[-1]
            )
        elif current_label_int == 48:
            new_section = (
                3
                if self.section_history.count(2) > len(self.section_history) / 2
                else self.section_history[-1]
            )
        elif current_label_int == 32:
            new_section = (
                4
                if self.section_history.count(3) > len(self.section_history) / 2
                else self.section_history[-1]
            )
        elif current_label_int == 8:
            new_section = (
                5
                if self.section_history.count(4) > len(self.section_history) / 2
                else self.section_history[-1]
            )
        else:
            new_section = self.section_history[-1] if self.section_history else 0

        self.section_history.append(new_section)
        if len(self.section_history) > self.window_size:
            self.section_history.pop(0)

        return new_section
