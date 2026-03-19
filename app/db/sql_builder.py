class SQLBuilder:
    def __init__(self):
        self.conditions: list[str] = []
        self.params: dict[str, object] = {}

    # 等于
    def eq(self, field: str, value, name: str | None = None):
        if value is None:
            return self
        name = name or field
        self.conditions.append(f"{field} = :{name}")
        self.params[name] = value
        return self

    # 模糊搜索
    def ilike(self, field: str, value: str | None, name: str | None = None):
        if not value:
            return self
        name = name or field
        self.conditions.append(f"{field} ILIKE :{name}")
        self.params[name] = f"%{value}%"
        return self

    # 范围
    def range(self, field: str, start, end, prefix: str):
        if start is not None:
            key = f"{prefix}_from"
            self.conditions.append(f"{field} >= :{key}")
            self.params[key] = start

        if end is not None:
            key = f"{prefix}_to"
            self.conditions.append(f"{field} <= :{key}")
            self.params[key] = end

        return self

    # OR搜索
    def search(self, keyword: str | None, fields: list[str], param="q"):
        if not keyword:
            return self

        or_sql = " OR ".join(f"{f} ILIKE :{param}" for f in fields)
        self.conditions.append(f"({or_sql})")
        self.params[param] = f"%{keyword}%"

        return self

    # 自定义条件
    def raw(self, sql: str):
        self.conditions.append(sql)
        return self

    # 生成SQL
    def build(self):
        where_sql = " AND ".join(self.conditions) if self.conditions else "TRUE"
        return where_sql, self.params