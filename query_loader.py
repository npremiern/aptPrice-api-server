def load_queries(file_path: str = "queries.sql"):
    queries = {}
    with open(file_path, "r", encoding="utf-8") as file:
        sql_key = None
        sql_value = []
        
        for line in file:
            line = line.strip()
            if not line or line.startswith("--"):
                continue
            
            if "=" in line:
                if sql_key:
                    queries[sql_key] = " ".join(sql_value)
                sql_key, sql_value = line.split("=", 1)
                sql_key = sql_key.strip()
                sql_value = [sql_value.strip()]
            else:
                sql_value.append(line.strip())

        if sql_key:
            queries[sql_key] = " ".join(sql_value)

    return queries

queries = load_queries()
