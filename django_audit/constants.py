from dataclasses import dataclass


@dataclass
class ChangeStatus:
    created: str = "Создание"
    updated: str = "Обновление"
    deleted: str = "Удаление"
