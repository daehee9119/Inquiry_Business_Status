# 표준 라이브러리
import configparser
from logging import Logger
# 3rd party
# 내부 패키지
from config import ConfigBean


def get_configs(my_logger: Logger):
    """
    지정된 config 파일을 읽어 config 객체를 리턴

    Parameters
    ----------
    my_logger : Logger
        수행 간 로그 기록용 객체
    Returns
    -------
    configparser.RawConfigParser
        *.ini 를 dict 형식으로 인덱싱 할 수 있는 config 객체
    """

    # *************CONFIG READ START*************
    # ini 파일 데이터를 적재할 config 객체 생성
    config = ''
    config_file = ConfigBean.CONFIG_FILE
    try:
        # ini 파일 읽기
        config = configparser.RawConfigParser()
        # 타입에 따라 읽어올 config 파일 정하기
        config.read(config_file, encoding='utf-8')
    except (IOError, ValueError):
        my_logger.error("Failed to load Config File! " + config_file)
        # config 파일이 없으면 프로그램 그냥 종료해야 함
        exit(-1)

    # *************CONFIG READ END*************
    return config


def get_parameters(param_str: str, argv_list: list, my_logger: Logger):
    """
    프로세스 수행에 필요한 파라미터 개수를 지정한 리스트만큼 가져와 리스트 값을 키로,
    가져온 파라미터값을 value 로 dict 를 만들어 반환
    sap 패키지만 사용, sap 패키지 리팩토링 후 삭제될 예정
    Deprecated

    Parameters
    ----------
    param_str : str
        어떤 프로세스의 파라미터 리스트를 가져와야 하는지 지정하는 str
    argv_list : list
        프로세스 수행에 필요한 파라미터 명을 리스트로 수령
    my_logger : Logger
        수행 간 로그 기록용 객체
    Returns
    -------
    dict
        ["리스트 element": "config 내 적재된 값", ...]
    """
    # *************PROCESS PARAM SETTING START*************
    my_logger.info("파라미터 가져오기")
    param_list = []
    param_map = {}

    if "," in param_str:
        param_list = param_str.split(",")
    else:
        param_list.append(param_str)

    if len(argv_list) != len(param_list):
        my_logger.error("Not enough parameters to run process! " +
                        "argv size = " + str(len(argv_list)) +
                        ", configured param size = " + str(len(param_list))
                        )
        # 없으면 그냥 종료해야 함
        exit(-1)

    for index in range(len(param_list)):
        # my_logger.info("param index " + str(index) + "=" + param_list[index] + "= " + argv_list[index])
        param_map[param_list[index]] = argv_list[index]
    # *************PROCESS PARAM SETTING END*************
    return param_map
