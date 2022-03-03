"""
Pandas extensions for resource resolver.
"""
import logging
from pathlib import Path
from typing import cast

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from ..core import get_resource_resolver

logger = logging.getLogger(__name__)


def get_pq_resource_as_dataframe(key: str, filters=[], **kwargs):
    resolver = get_resource_resolver()

    logger.debug(f'Getting path for resource {key}')
    resource_path = Path(resolver.get(key, as_a='str'))

    df = cast(pd.DataFrame, pd.read_parquet(resource_path, engine='pyarrow',
                                            filters=filters, **kwargs))
    if hasattr(df, 'columns'):
        logger.debug(f'Dataframe from {key} has columns {list(df.columns)}.')
    if hasattr(df, 'size'):
        logger.debug(f'Dataframe from {key} has size {df.size}.')
    return df


def append_dataframe_pq(key: str,
                        df: pd.DataFrame):

    resolver = get_resource_resolver()
    logger.debug(f'Getting path for resource {key}')
    root_path = Path(resolver.get(key, as_a='str'))
    logger.debug(f'Root path is: {root_path}.')

    logger.debug('Dataframe head:')
    logger.debug(df.head())

    logger.debug(f'Appending {df.size} rows to resource {key}.')

    table = pa.Table.from_pandas(df)

    pq.write_to_dataset(table=table, root_path=root_path)


def get_csv_resource_as_dataframe(key: str, encoding='utf-8', **kwargs) -> pd.DataFrame:
    resolver = get_resource_resolver()

    logger.debug(f'Getting file handle for resource {key}')
    resource = resolver.get(key, as_a='file_handle')

    df = cast(pd.DataFrame, pd.read_csv(
        resource, engine='python', encoding=encoding, **kwargs))
    if hasattr(df, 'columns'):
        logger.debug(f'Dataframe from {key} has columns {list(df.columns)}.')
    if hasattr(df, 'size'):
        logger.debug(f'Dataframe from {key} has size {df.size}.')

    return df


def save_dataframe_csv(key: str, df: pd.DataFrame, encoding='utf-8', **kwargs) -> None:
    resource_resolver = get_resource_resolver()

    handle = resource_resolver.get(key, as_a='file_handle')
    handle.seek(0, 0)

    logger.debug(f"Retrieved file handle for '{key}': '{handle}'.")

    df.to_csv(handle, encoding=encoding, **kwargs)  # type: ignore
    logger.debug(f"Wrote {handle.tell()} bytes to resource {key}.")


def append_dataframe_csv(key: str, df: pd.DataFrame,
                         index: bool = False,
                         header: bool = False,
                         encoding: str = 'utf-8',
                         **kwargs) -> int:
    resource_resolver = get_resource_resolver()

    handle = resource_resolver.get(key, as_a='file_handle')
    handle.seek(0, 2)

    size = handle.tell()

    logger.debug(f"Retrieved file handle for '{key}': '{handle}'.")

    df.to_csv(handle, mode='a+', index=index, header=header,  # type: ignore
              encoding=encoding, **kwargs)

    diff = handle.tell() - size
    logger.debug(f"Wrote {diff} bytes to resource {key}.")

    return diff
