import os
import asyncpg as apg
from loader import logger
from asyncpg.exceptions import UndefinedTableError, InterfaceError
import time
import json
import asyncio


async def convert_data(data: list, fetchone=False):
    res = []
    for x in data:
        res.append(dict(x))
    if len(res) == 0:
        if not fetchone:
            return []
        return None
    if fetchone:
        return res[0]
    return res


class PostSQLDB:

    def __init__(self, _db_name, _db_user, _db_pass, _db_host):
        self.db_name = _db_name
        self.db_user = _db_user
        self.db_pass = _db_pass
        self.db_host = _db_host
        self.connection = None
        self.users_table_columns = (
            ('user_id', 'BIGINT PRIMARY KEY'),
            ('status', 'VARCHAR(255)'),
            ('time_registered', 'FLOAT'),
        )
        self.personal_table_columns = (
            ('personal_id', 'SERIAL PRIMARY KEY'),
            ('name', 'VARCHAR(255)'),
            ('last_name', 'VARCHAR(255)'),
            ('middle_name', 'VARCHAR(255)'),
            ('full_name', 'VARCHAR(765)'),
            ('project', 'VARCHAR(255)'),
            ('position', 'VARCHAR(255)'),
            ('avatar_path', 'VARCHAR(255)'),
            ('time_join', 'FLOAT'),
            ('time_registered', 'FLOAT'),
        )

    # ====== SERVICE METHODS ======

    async def connect(self):
        self.connection = await apg.connect(database=self.db_name, user=self.db_user, password=self.db_pass,
                                            host=self.db_host)

    async def check_db_structure(self):
        async def repair_table(table_name, columns_data):
            try:
                await self.connection.execute(f'SELECT 1 FROM {table_name};')
                for name, typ in columns_data[1::]:
                    await self.connection.execute(f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS {name} {typ};")
            except UndefinedTableError:
                logger.info(f'[DB_REPAIR] Table {table_name} not found, creating new table...')
                columns = ''
                for name, typ in columns_data:
                    columns = columns + name + ' ' + typ + ', '
                await self.connection.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns[0:-2]});")
                logger.info(f'[DB_REPAIR] Table {table_name} successfully created')

        # Check / Repair all tables
        await repair_table('users', self.users_table_columns)
        await repair_table('personal', self.personal_table_columns)
        logger.info('Successfully check db structure')

    async def execute(self, sql, rerun=False, fetch=False, fetchone=False):
        try:
            if fetch:
                return await convert_data(await self.connection.fetch(sql), fetchone)
            else:
                return await self.connection.execute(sql)
        except UndefinedTableError as ex:
            logger.warning(f'Table not found error, trying to solve... (errmsg: {ex}, sql: {sql})')
            await self.check_db_structure()
            if not rerun:
                await self.execute(sql, rerun=True, fetch=fetch)
            else:
                logger.error(
                    f'Cant solve db error, please check if database works correctly. (errmsg: {ex}, sql: {sql})')
                return None
        except InterfaceError as ex:
            if 'another operation is in progress' in str(ex):
                logger.info(f"another db operation in progress, waiting 1sec and trying again... (sql: {sql})")
                await asyncio.sleep(1)
                await self.execute(sql, rerun=True, fetch=fetch)
        except Exception as ex:
            logger.error(f'Error while executing db method. (errmsg: {ex}, sql: {sql})', exc_info=True)
            raise

    async def fetch(self, sql):
        return await self.execute(sql, fetch=True)

    async def fetchone(self, sql):
        return await self.execute(sql, fetch=True, fetchone=True)

    # ====== DB METHODS ======

    # === Users ===

    async def get_user(self, user_id: int):
        return await self.fetchone(f"SELECT * FROM users WHERE user_id = {user_id};")

    async def get_users(self):
        return await self.fetch(f"SELECT * FROM users;")

    async def add_user(self, user_id: int):
        return await self.execute(
            f"INSERT INTO users (user_id, time_registered, status) "
            f"VALUES({user_id}, {time.time()}, 'active');")

    async def set_user_status(self, user_id: int, value: str):
        return await self.execute(f"UPDATE users SET status = '{value}' WHERE user_id = {user_id};")

    # === Personal ===

    async def get_personal(self, active: bool = True):
        if active:
            return await self.fetch(f"SELECT * FROM personal WHERE status = 'active';")
        return await self.fetch(f"SELECT * FROM personal;")

    async def get_personal_by_id(self, personal_id: int):
        return await self.fetchone(f"SELECT * FROM personal WHERE personal_id = {personal_id};")

    # Защита от SQL инъекций не требуется, так как имеется встроенная, в самой библиотеке для работы с базой данных
    # (https://github.com/MagicStack/asyncpg/issues/822).

    async def get_personal_by_name(self, name: str, active: bool = True):
        if active:
            return await self.fetchone(f"SELECT * FROM personal WHERE {name} IN full_name AND status = 'active';")
        return await self.fetchone(f"SELECT * FROM personal WHERE {name} IN full_name;")

    async def add_personal(self, first_name: str, last_name: str, middle_name: str, position: str,
                           project: str, time_join: float, avatar: str = 'None'):
        return await self.fetchone(f"INSERT INTO personal (first_name, last_name, middle_name, position, project, "
                                   f"time_join, avatar) VALUES('{first_name}', '{last_name}', '{middle_name}', "
                                   f"'{position}', '{project}', {time_join}, '{avatar}') RETURNING personal_id;")
