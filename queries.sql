-- 서비스 ID로 두 개의 테이블을 조인하여 데이터 조회
GET_SERVICE_DATA=SELECT 법정동코드 AS "legalCd", 도로명주소 AS "roadAddr", 시도 AS "sido", 시군구 AS "sigungu", 읍면 AS "emd", 동리 AS "ri", CASE WHEN 특수지코드 = '0' THEN '1' WHEN 특수지코드 = '1' THEN '2' WHEN 특수지코드 = '2' THEN '3' WHEN 특수지코드 = '6' THEN '5' ELSE 특수지코드 END AS "spCd", 본번 AS "bon", 부번 AS "boo", 특수지명 AS "spNm", 단지명 AS "cmpNm", 동명 AS "dongNm", 호명 AS "hoNm", 전용면적 AS "exArea", 공시가격 AS "pubPrice", 단지코드 AS "cmpCd", 동코드 AS "dongCd", 호코드 AS "hoCd", 건축물대장PK AS "bldbLedgerPK", "(구)건축물대장PK" AS "oldBldbLedgerPK", PNU AS "PNU" FROM housing_prices hp WHERE hp.도로명주소 LIKE '%' || $1 || '%';

-- 건축물대장 조회
GET_BUILDING_LEDGER=SELECT 법정동코드 AS "legalCd", 도로명주소 AS "roadAddr", 시도 AS "sido", 시군구 AS "sigungu", 읍면 AS "emd", 동리 AS "ri", CASE WHEN 특수지코드 = '0' THEN '1' WHEN 특수지코드 = '1' THEN '2' WHEN 특수지코드 = '2' THEN '3' WHEN 특수지코드 = '6' THEN '5' ELSE 특수지코드 END AS "spCd", 본번 AS "bon", 부번 AS "boo", 특수지명 AS "spNm", 단지명 AS "cmpNm", 동명 AS "dongNm", 호명 AS "hoNm", 전용면적 AS "exArea", 공시가격 AS "pubPrice", 단지코드 AS "cmpCd", 동코드 AS "dongCd", 호코드 AS "hoCd", 건축물대장PK AS "bldbLedgerPK", "(구)건축물대장PK" AS "oldBldbLedgerPK", PNU AS "PNU" FROM housing_prices hp WHERE hp.건축물대장pk = $1;

-- PNU 단건 조회
GET_PNU_DATA=SELECT 법정동코드 AS "legalCd", 도로명주소 AS "roadAddr", 시도 AS "sido", 시군구 AS "sigungu", 읍면 AS "emd", 동리 AS "ri", CASE WHEN 특수지코드 = '0' THEN '1' WHEN 특수지코드 = '1' THEN '2' WHEN 특수지코드 = '2' THEN '3' WHEN 특수지코드 = '6' THEN '5' ELSE 특수지코드 END AS "spCd", 본번 AS "bon", 부번 AS "boo", 특수지명 AS "spNm", 단지명 AS "cmpNm", 동명 AS "dongNm", 호명 AS "hoNm", 전용면적 AS "exArea", 공시가격 AS "pubPrice", 단지코드 AS "cmpCd", 동코드 AS "dongCd", 호코드 AS "hoCd", 건축물대장PK AS "bldbLedgerPK", "(구)건축물대장PK" AS "oldBldbLedgerPK", PNU AS "PNU" FROM housing_prices hp WHERE hp.pnu = $1;

-- 시도 목록 조회
GET_SIDO_LIST=SELECT DISTINCT 시도코드 AS "sidoCd", 시도 AS "sido" FROM ADDR_STEP ORDER BY 시도코드;

-- 시군구 목록 조회
GET_SIGUNGU_LIST=SELECT DISTINCT 시도코드 AS "sidoCd", 시도 AS "sido", 시군구코드 AS "sigunguCd", 시군구 AS "sigungu" FROM ADDR_STEP WHERE 시도코드 = $1 ORDER BY 시군구;

-- 읍면동 목록 조회
GET_EMD_LIST=SELECT DISTINCT 시도코드 as "sidoCd", 시도 as "sido", 시군구코드 as "sigunguCd", 시군구 as "sigungu", 읍면코드 as "emdCd", CASE WHEN 읍면 = '' THEN 동리 ELSE 읍면 END AS "emd", 동리코드 as "riCd", CASE WHEN 읍면 = '' THEN '' ELSE 동리 END AS "ri" FROM ADDR_STEP WHERE 시군구코드 LIKE $1 || '%' ORDER BY emd, ri;

-- 동리 목록 조회
GET_RI_LIST=SELECT DISTINCT 시도코드 AS "sidoCd", 시도 as "sido", 시군구코드 AS "sigunguCd", 시군구 as "sigungu", 읍면코드 AS "emdCd", 읍면 as "emd", 동리코드 AS "riCd", 동리 as "ri" FROM ADDR_STEP WHERE 읍면코드 LIKE $1 || '%' ORDER BY ri;