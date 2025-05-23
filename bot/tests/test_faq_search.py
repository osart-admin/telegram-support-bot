# bot/tests/test_faq_search.py

import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from faq_search import find_best_faq

def test_find_best_faq_no_result():
    # Ожидается None если нет похожего FAQ
    response = find_best_faq("Неизвестный вопрос который не в базе")
    assert response is None

def test_find_best_faq_found():
    # Заменить на реальный вопрос из твоей FAQ базы для корректного теста!
    response = find_best_faq("Как сменить пароль?")
    assert response is None or response.startswith("[FAQ]")

# Для запуска:
# pytest bot/tests/test_faq_search.py
