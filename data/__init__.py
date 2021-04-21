import os


class DataBean:
    ABS_PATH = os.path.dirname(os.path.abspath(__file__))
    INPUT_ABS_PATH = ABS_PATH + "\\Input"
    OUTPUT_ABS_PATH = ABS_PATH + "\\Output"

    """
    data 폴더 내 데이터 접근을 위한 경로 관리용 init 모듈

    Attributes
    -----------
    ABS_PATH : str
        data 폴더의 절대 경로
    INPUT_ABS_PATH : str
        Input 이미지 파일 경로
    OUTPUT_ABS_PATH : str
        수행 결과 txt 를 적재할 Output 경로
    """

