from typing import cast

import pandas as pd
import pytest

from resource_resolver import ResourceResolver
from resource_resolver.utils.pandas import (
     append_dataframe_csv
)


@pytest.fixture(scope='module')
def test_dataframe():
    return pd.DataFrame({
        'team': ['Green', 'Red', 'Blue', 'Orange'],
        'score': [100, 200, 300, 400],
        'size': [4, 6, 3, 4]
    })


@pytest.fixture
def test_resolver(test_dataframe: pd.DataFrame):
    resolver = ResourceResolver()
    resolver.define('test_dataframe')
    handle = resolver.get('test_dataframe', as_a='file_handle')
    handle.seek(0, 0)
    handle.truncate()

    assert test_dataframe.shape[0] == 4
    test_dataframe.to_csv(handle, index=False)  # type: ignore

    return resolver


def test_append_csv_adds_rows(test_resolver, test_dataframe):
    fh = test_resolver.get(
        'test_dataframe', as_a='file_handle')
    print(fh.read())

    append_dataframe_csv('test_dataframe', test_dataframe, context=test_resolver
                            )

    fh = test_resolver.get(
        'test_dataframe', as_a='file_handle')
    print(fh.read())
    fh.seek(0, 0)
    df = cast(pd.DataFrame, pd.read_csv(fh))

    assert df.shape[0] == 8
