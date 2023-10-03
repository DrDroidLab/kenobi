from typing import List

import clickhouse_connect.driver


class TableProxy:
    data_columns: List[str] = None
    data_columns_types: List[str] = None
    table_name: str = None

    def __init__(self, client: clickhouse_connect.driver.Client):
        if not self.data_columns or not self.data_columns_types or not self.table_name:
            raise NotImplementedError
        self.client = client

    def describe_table(self):
        result = self.client.query(f'DESCRIBE TABLE {self.table_name}')
        print(result.column_names[0:2])
        print(result.result_columns[0:2])

    def insert_data(self, data):
        self.client.insert(
            self.table_name,
            data,
            column_names=self.data_columns,
            column_type_names=self.data_columns_types
        )
