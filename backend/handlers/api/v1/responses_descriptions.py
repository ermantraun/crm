lead_responses = {
    "create": {
        201: {"description": "Лид создан"},
        200: {"description": "OK"}, #если лид уже существует
        422: {"description": "Некорректные данные лида"},
    },
    "get": {
        200: {"description": "Лид найден"},
        404: {"description": "Лид не найден"},
    },
}
common_responses = {
    500: {"description": "Внутренняя ошибка"},
}
