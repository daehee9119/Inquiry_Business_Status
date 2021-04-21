import os


class LogBean:
    """
    logs 폴더 내 데이터 접근을 위한 경로 관리용 init 모듈

    Attributes:
    -------
    ABS_PATH : str
        logs 폴더의 절대 경로

    See Also
    ----------
    python_rpa.log:
        rpa 수행 로그 (금일)
    python_rpa.log_yyyyMMdd:
        rpa 수행 로그 (과거)
    py_batch_2021_02_09.log:
        배치 프로세스 수행 로그
    """
    ABS_PATH = os.path.dirname(os.path.abspath(__file__))
