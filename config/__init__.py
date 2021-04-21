import os


class ConfigBean:
    ABS_PATH = os.path.dirname(os.path.abspath(__file__))
    CONFIG_FILE = ABS_PATH + '\\config.ini'

    """
    config 폴더 내 데이터 접근을 위한 경로, 파일명 관리용 init 모듈

    Attributes
    ------------
    ABS_PATH : str
        Config 패키지의 절대 경로
    CONFIG_FILE : str
        config.ini 파일의 절대 경로 + 파일명

    See Also
    ----------
    config.ini.template:
        배포 시 사용될 ini template, 배포 후 개인 정보, 계정 정보를 수동으로 업데이트 할 것
    *.json:
        GCP Vision API 사용 시 Authentication 을 위한 JSON Key 파일
    """