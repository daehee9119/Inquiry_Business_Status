# 표준 라이브러리
import configparser
import platform
import logging
import logging.handlers
# 3rd party
# 내부 패키지
from config import ConfigBean
from logs import LogBean


def create_logger(log_type):
    """
    지정된 로그 타입에 따라 config 파일 내 로그 설정에 따른 로깅 객체 반환

    Parameters
    ----------
    log_type : str
        현재는 "RPA_LOG" 만 존재, 만일 다른 system 로그 파일 필요 시 system.ini 내 섹션 추가 필요

    Returns
    -------
    logging.Logger
        생성한 로깅 객체
    """
    # *************CONFIG READ START*************
    # ini 파일 데이터를 적재할 config 객체 생성
    logging_dict = ''
    try:
        # ini 파일 읽기
        config = configparser.RawConfigParser()
        config.read(ConfigBean.CONFIG_FILE, encoding='utf-8-sig')
        # 섹션별 dict 처리
        logging_dict = config[log_type]
    except IOError:
        print("Failed to load Config File! (", ConfigBean.CONFIG_FILE, ") ")
        # config 파일이 없으면 프로그램 그냥 종료해야 함
        exit(-1)
    # *************CONFIG READ END*************

    # *************LOGGING CONFIG START*************
    # 로그 관련 설정값 가져오기
    logger = logging_dict["logger_name"]
    file_name = LogBean.ABS_PATH + "\\" + logging_dict["file_name"]
    log_format = logging_dict["log_format"]
    start_time = logging_dict["start_time"]
    interval = int(logging_dict["interval"])
    backup = int(logging_dict["backup"])

    # 로그 객체 생성
    my_logger = logging.getLogger(logger)

    # 이미 핸들러가 있다면 생성된 것이니까 그대로 돌려준다
    if len(my_logger.handlers) > 0:
        return my_logger

    my_logger.setLevel(logging.INFO)

    # 로그 파일 핸들러를 작성하여 이 규칙에 맞게 파일 관리되도록 지정
    file_handler = logging.handlers.TimedRotatingFileHandler(filename=file_name,
                                                             when=start_time,
                                                             interval=interval,
                                                             backupCount=backup,
                                                             encoding='utf-8'
                                                             )
    # 파일명 형식에 날짜 추가(백업 파일 간 구분용)
    file_handler.suffix = '_%Y%m%d.log'
    # 포맷 추가 = 로그 시간|레벨명|로그이름|파일명|라인번호 >> 메시지
    file_handler.setFormatter(logging.Formatter(log_format))

    # 콘솔 출력용 핸들러 작성
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format))
    console_handler.setLevel(logging.DEBUG)

    # 혹시 로그 사용 시 자식 프로세스가 핸들러를 물고 있지 않도록 설정
    if platform.system() == 'Windows':
        import msvcrt
        import win32api
        import win32con
        win32api.SetHandleInformation(msvcrt.get_osfhandle(file_handler.stream.fileno()),
                                      win32con.HANDLE_FLAG_INHERIT, 0)

    # 핸들러를 로그 객체에 적용
    my_logger.addHandler(file_handler)
    my_logger.addHandler(console_handler)
    # *************LOGGING CONFIG END*************
    my_logger.info("Created Logger")
    return my_logger
