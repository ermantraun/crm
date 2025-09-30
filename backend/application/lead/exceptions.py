class LeadNotFoundException(Exception):
    """Исключение, возникающее при попытке доступа к несуществующему лиду."""
    pass

class InsightNotFoundException(Exception):
    """Исключение, возникающее при попытке доступа к несуществующему инсайту."""
    pass

class LeadAlreadyExistsException(Exception):
    """Исключение, возникающее при попытке создать лид, который уже существует."""
    pass

class InsightAlreadyExistsException(Exception):
    """Исключение, возникающее при попытке создать инсайт, который уже существует."""
    pass

class InvalidLeadDataException(Exception):
    """Исключение, возникающее при предоставлении некорректных данных лида."""
    pass

class InvalidInsightDataException(Exception):
    """Некорректные данные инсайта (пустые / отсутствующие строки)."""
    pass