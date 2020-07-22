# Configuration
## 사용할 API KEY 설정
1. *./config/bs_config.ini*하단 경로에 존재하는 파일 열람. (폴더명/파일명은 변경하면 안됨)  
2. [Inquiry_Business_Status.py] 섹션의 API_KEY키를 위한 값 설정.  
   -> Google Cloud Vision API 설정 시 받는 KEY를 JSON으로 받아 경로와 파일명을 값으로 설정  
   ex. API_KEY = ./API_KEY/xxx.json  
  
3. 저장 및 종료

## 결과 파일이 적재될 폴더 변경 원할 경우
- [Inquiry_Business_Status.py] 섹션의 Result 키에 할당된 값을 변경.  
---------------------------------------
# Data Set Preperation
## 실행 시 Input으로 쓰일 이미지 파일 적재
1. 파이썬 스크립트 경로에 Data_Set 폴더 생성    
2. 해당 폴더 내 수집 대상인 사업자 등록증 이미지 파일들을 모두 ./Data_Set 폴더 내 적재    
   * 이미지 해상도가 낮으면 OCR Confidence가 낮을 수 있습니다.  

## Output
- config.ini 파일에서 설정한 Result 키값에 할당된 경로로 결과 파일이 저장됨  
  1. [이미지파일명]_result.txt = 해당 이미지 파일의 OCR 결과 (이미지 내 텍스트 전문)  

  2. total_result.txt = 파일별 OCR 결과에서 사업자 등록증 번호를 추출하여 홈택스에 휴폐업 조회한 결과  
                        (파일명, 추출한 사업자 등록 번호, 등록 유형, 휴폐업 상태)  


## 사후 데이터 유효성 검증
- OCR을 무조건 믿을 수 없음으로, total_result.txt 파일에 적힌 휴폐업 조회 시 사용한 사업자 등록번호와   
  이미지 상 실제 사업자 등록 번호가 같은 지 확인 필수
