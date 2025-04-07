def load_queries(file_path):
    queries = {}
    current_query_id = None
    current_query = []
    in_multiline = False
    delimiter = None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            # 주석 무시
            if line.startswith('--') or not line:
                continue
                
            # 여러 줄 쿼리 시작 확인
            if '=<<' in line and not in_multiline:
                parts = line.split('=<<', 1)
                current_query_id = parts[0].strip()
                delimiter = parts[1].strip()
                in_multiline = True
                current_query = []
                continue
                
            # 여러 줄 쿼리 종료 확인
            if in_multiline and line == delimiter:
                queries[current_query_id] = '\n'.join(current_query)
                in_multiline = False
                continue
                
            # 여러 줄 쿼리 내용 추가
            if in_multiline:
                current_query.append(line)
                continue
                
            # 일반 한 줄 쿼리 처리
            if '=' in line and not in_multiline:
                parts = line.split('=', 1)
                query_id = parts[0].strip()
                query = parts[1].strip()
                queries[query_id] = query
                
    return queries

queries = load_queries("queries.sql")
