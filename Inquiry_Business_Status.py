# 표준 라이브러리
import os
import re
import io
import sys
# 3rd party
import requests
import Cloud_Vision
# 내부 패키지
from utils.utils_config import get_configs
from utils.utils_logs import create_logger
from utils.utils_io import make_dir

from config import ConfigBean
from data import DataBean


def extract_bsn(target_str):
    """
    Vision API 결과값에서 사업자 등록 번호를 패턴에 따라 정규표현식을 사용하여 추출
    :param target_str: 정규표현식을 적용할 원본 String
    :return: 추출한 사업자 등록 번호, 없을 경우 None이 return 됨
    """
    p = re.compile(pattern='(?P<bsn>\d{3}-\d{2}-\d{5})')
    bsn = None
    try:
        match_test = p.search(target_str)
        if match_test is not None:
            bsn = match_test.group('bsn')
    except Exception as e:
        print(e)
    finally:
        return bsn


def send_hometax(bsn):
    """
    추출한 사업자 등록 번호를 홈텍스 내부 API에 담아 보내 해당 사업자의 상태를 조회
    :param bsn: API에 송신할 사업자 등록 번호
    :return: API의 결과값을 String으로 반환
    """
    body_template = """<map id='ATTABZAA001R08'>
            <pubcUserNo/>
            <mobYn>N</mobYn>
            <inqrTrgtClCd>1</inqrTrgtClCd>
            <txprDscmNo>[사업자번호]</txprDscmNo>
            <dongCode>__MIDDLE__</dongCode>
            <psbSearch>Y</psbSearch>
            <map id='userReqInfoVO'/>
        </map>"""
    headers = {'Content-Type': 'application/xml'}
    hometax_url = 'https://teht.hometax.go.kr/wqAction.do?actionId=ATTABZAA001R08&screenId=UTEABAAA13&popupYn=false' \
                  '&realScreenId='

    # 홈택스에 XML 요청
    if bsn is not None:
        body = body_template.replace("[사업자번호]", bsn.replace("-", ""))
        response = requests.post(url=hometax_url, headers=headers, data=body)
        return_text = ""
        if not response.ok:
            raise Exception('{}'.format(response.text))
        else:
            return_text = response.text

        return return_text


def extract_status(target_str):
    """
    홈텍스 API에서 수신한 결과값에서 특정 태그에 달린 상태/설명 문자열을 추출하여 리스트 객체에 담아 리턴함
    :param target_str: 홈텍스 API로부터 수신한 String
    :return: 추출한 상태/설명을 담은 리스트 객체
    """
    p = re.compile(pattern='<smpcBmanTrtCntn>(?P<status>[^<]+).+<trtCntn>(?P<desc>[^<]+)', flags=re.UNICODE)
    status = None
    desc = None
    try:
        match_test = p.search(target_str)
        if match_test is not None:
            status = match_test.group('status')
            desc = match_test.group('desc')
    except Exception as e:
        print(e)
    finally:
        return [status, desc]


# ######################MAIN STREAM###################### #
if __name__ == '__main__':
    # 로깅 객체 생성
    my_logger = create_logger("RPA_LOG")
    # locale.setlocale(locale.LC_TIME, 'ko_KR.UTF-8')
    # 리턴용 string
    ret_str = 'NA'

    # ini 파일을 읽어올 config 객체 생성
    config_dict = get_configs(my_logger)["MAIN"]

    # API 사용을 위한 인증 정보를 환경 변수에 설정
    # 그냥 환경변수에 설정하면 원인 모를 이유로 python 실행 시 가져오지 못함
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ConfigBean.ABS_PATH + "\\" + config_dict['API_KEY']
    # Vision API에 요청할 사업자 등록증 이미지를 담은 경로
    img_path = DataBean.INPUT_ABS_PATH
    result_path = DataBean.OUTPUT_ABS_PATH

    if not make_dir([img_path, result_path], my_logger):
        my_logger.error("Input, Output 경로 생성 실패")
        sys.exit(-1)

    # 경로 내 모든 이미지 파일 순회
    result_str = ""
    for img_file in os.listdir(img_path):
        # Google Cloud Vision에 요청하여 이미지를 텍스트로 변환
        total_str = Cloud_Vision.detect_img_text(img_path + img_file)
        print(total_str)
        # 정규표현식을 사용해 텍스트 중 사업자 등록 번호 추출
        result_bsn = extract_bsn(total_str)
        # 홈택스에 사업자 등록번호를 이용해 휴폐업 상태 요청
        result_res = send_hometax(result_bsn)
        # 요청 결과값에서 상태와 설명만 추출
        result_status = extract_status(result_res)
        with io.open(result_path + img_file + '_result.txt', 'w', encoding="utf-8") as f:
            f.write(total_str)
        # 프로젝트 root 경로에 이미지 파일별 txt 생성
        result_str += "Img File: " + img_file + \
                      "\nBusiness Number: " + result_bsn + \
                      "\nstatus: " + result_status[0] + \
                      "\ndesc: " + result_status[1] + \
                      '\n\n'

    # 결과값이 존재할 때만 만들 것
    if result_str != "":
        with io.open(result_path + 'total_result.txt', 'w', encoding="utf-8") as f:
            f.write(result_str)
