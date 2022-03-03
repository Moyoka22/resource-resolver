import logging

import pytest

@pytest.fixture(autouse=True)
def log_test_name(request):
    test_name = request.node.name
    logging.debug(test_name)
