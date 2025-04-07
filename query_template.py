import re
from typing import Dict, Any, List, Tuple

def parse_template(template: str, params: Dict[str, Any]) -> Tuple[str, List[Any]]:
    """
    조건부 쿼리 템플릿을 파싱하여 실행 가능한 쿼리와 매개변수 목록을 반환합니다.
    
    예시 템플릿:
    ```
    SELECT * FROM table
    WHERE condition1 = $1
    {% if param2 %}
    AND condition2 = $2
    {% endif %}
    {% if param3 %}
    AND condition3 = $3
    {% endif %}
    ```
    """
    # if 블록 찾기
    if_pattern = r'{%\s*if\s+(\w+)\s*%}(.*?)(?:{%\s*endif\s*%})'
    
    # 매개변수 목록
    query_params = []
    param_index = 1
    
    # 기본 쿼리 (첫 번째 매개변수는 항상 포함)
    query = template
    query_params.append(params.get('legalCode'))
    
    # if 블록 처리
    for match in re.finditer(if_pattern, template, re.DOTALL):
        param_name = match.group(1)
        block_content = match.group(2)
        
        if param_name in params and params[param_name]:
            # 매개변수가 존재하면 블록 내용 유지하고 매개변수 추가
            param_index += 1
            query_params.append(params[param_name])
            # $n을 실제 인덱스로 대체
            block_content = re.sub(r'\$\d+', f'${param_index}', block_content)
        else:
            # 매개변수가 없으면 블록 제거
            query = query.replace(match.group(0), '')
    
    # if 블록 태그 제거
    query = re.sub(r'{%.*?%}', '', query)
    
    return query, query_params 