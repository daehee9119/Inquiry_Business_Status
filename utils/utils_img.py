# 표준 라이브러리
import os
from io import BytesIO
import traceback
from logging import Logger
import shutil
# 3rd party
from PIL import Image
from pdf2image import convert_from_path
import numpy as np
import requests
# 내부 패키지
from utils.utils_io import is_duplicated


def is_img(target_file: str, logger: Logger):
    """
    파일 형태인지, 이미지 확장자를 가지고 있는지 검증

    Parameters
    ----------
    target_file : str
        이미지 검증할 파일 (경로 포함)
    logger: Logger
        사용할 로깅 객체

    Returns
    -------
    bool
        이미지 여부
    """
    if not os.path.isfile(target_file):
        return False
    # 검증할 확장자명
    extension_list = ['png', 'jpeg', 'jpg']
    for extension in extension_list:
        if target_file.lower().endswith(extension):
            return True
    logger.error("이미지 파일이 아닙니다! - " + target_file)
    return False


def crop_img(filename: str, x_rate: float, y_rate: float, my_logger: Logger):
    """
    x, y 비율만큼 이미지를 잘라 같은 이름으로 저장

    Parameters
    ----------
    filename : str
        원본 이미지 객체의 파일명, 경로
    x_rate : float
        남겨둘 x 영역 비율
    y_rate : float
        남겨둘 Y 영역 비율
    my_logger : Logger
        사용할 로깅 객체

    Returns
    -------
    bool
        crop 성공 여부
    """
    if not is_img(filename, my_logger):
        return False

    # cv2로 읽은 이미지 객체 만들기
    src_img = Image.open(filename)
    if src_img is None:
        return False
    src_arr = np.array(src_img)
    heights, width, = [len(src_arr), len(src_arr[0])]

    # pixel 배열을 슬라이스하여 이미지 자르기
    cropped_arr = src_arr[0:int(heights * y_rate), 0:int(width * x_rate)]
    Image.fromarray(cropped_arr).save(filename)

    return is_img(filename, my_logger)


def crop_img_row(source_file, y1: int, y2: int, my_logger):
    """
    y1 - y2 좌표만큼 이미지를 잘라 같은 이름으로 저장

    Parameters
    ----------
    source_file : str
        원본 이미지 객체의 파일명, 경로
    y1 : int
        잘라내기 시작하는 y 좌표
    y2 : int
        잘라내기 종료할 y 좌표
    my_logger : Logger
        사용할 로깅 객체

    Returns
    -------
    bool
        crop 성공 여부
    """
    if not is_img(source_file, my_logger):
        return False
    # 덮어쓸 이미지 모드를 동일하게 설정
    source_img = Image.open(source_file).convert('RGBA')
    src_arr = np.array(source_img)
    src_arr = np.delete(src_arr, range(y1, y2), axis=0)
    cropped_img = Image.fromarray(src_arr)
    cropped_img.save(source_file)
    return is_img(source_file, my_logger)


def crop_img_col(source_file, x1: int, x2: int, my_logger):
    """
    x1 - x2 좌표만큼 이미지를 잘라 같은 이름으로 저장

    Parameters
    ----------
    source_file : str
        원본 이미지 객체의 파일명, 경로
    x1 : int
        잘라내기 시작하는 x 좌표
    x2 : int
        잘라내기 종료할 x 좌표
    my_logger : Logger
        사용할 로깅 객체

    Returns
    -------
    bool
        crop 성공 여부
    """
    if not is_img(source_file, my_logger):
        return False
    # 덮어쓸 이미지 모드를 동일하게 설정
    source_img = Image.open(source_file).convert('RGBA')
    src_arr = np.array(source_img)
    src_arr = np.delete(src_arr, range(x1, x2), axis=0)
    cropped_img = Image.fromarray(src_arr)
    cropped_img.save(source_file)
    return is_img(source_file, my_logger)


def merge_img_row(source_file: str, overlap_file: str, save_file: str, my_logger: Logger,
                  x_offset: int = 0, y_offset: int = 0):
    """
    source file 위에 overlap_file 을 x, y offset 에 맞추어 덮어쓴 후 save_file 에 따라 저장

    Parameters
    ----------
    source_file : str
        원본 이미지 객체의 파일명, 경로
    overlap_file : str
        덮어쓸 이미지 파일명, 경로
    save_file : str
        저장할 이미지 파일명, 경로
    my_logger : Logger
        사용할 로깅 객체
    x_offset : int
        덮어쓸 이미지의 배경 대비 x offset 크기
    y_offset : int
        덮어쓸 이미지의 배경 대비 y offset 크기

    Returns
    -------
    bool
        merge 성공 여부
    """
    if not is_img(source_file, my_logger) or not is_img(overlap_file, my_logger):
        return False

    try:
        # 덮어쓸 이미지 모드를 동일하게 설정
        source_img = Image.open(source_file).convert('RGBA')
        overlap_img = Image.open(overlap_file).convert('RGBA')

        canvas = Image.new("RGBA", source_img.size)
        canvas.paste(source_img, (0, 0), source_img)
        canvas.paste(overlap_img, (x_offset, y_offset), overlap_img)
        canvas.save(save_file)
        return True
    except Exception as e:
        print(e)
        return False


def resize_img(img_file: str, width: int, height: int, img_format: str, save_file: str, my_logger):
    """
    지정된 너비/높이로 이미지 리사이즈 및 다른이름 저장

    Parameters
    ----------
    img_file : str
        원본 이미지 객체의 파일명, 경로
    width : int
        리사이즈 너비
    height : int
        리사이즈 높이
    img_format : str
        리사이즈 저장 시 적용할 이미지 포맷
    save_file : str
        저장할 이미지 파일명/경로
    my_logger : Logger
        사용할 로깅 객체

    Returns
    -------
    bool
        resize 성공 여부
    """
    if not is_img(img_file, my_logger):
        return False

    if img_format.lower() not in ['png', 'jpeg']:
        my_logger.error("지정할 수 있는 포맷은 png, jpeg 뿐입니다! - " + img_format.lower())
        return False

    img = Image.open(img_file)
    resized_img = img.resize((width, height))
    resized_img.save(save_file, img_format, quality=95)

    if not is_img(save_file, my_logger):
        my_logger.error("이미지 파일이 생성되지 않았습니다! - " + save_file)
        return False
    else:
        return True


def get_img_from_url(url: str, save_file: str, img_format: str, my_logger: Logger):
    """
    지정된 URL 기반 이미지 추출

    Parameters
    ----------
    url : str
        이미지를 가져올 url
    save_file : str
        저장할 파일명, 경로
    img_format : str
        저장할 이미지 확장자명
    my_logger : Logger
        사용할 로깅 객체

    Returns
    -------
    bool
        이미지 저장 성공 여부
    """
    try:
        res = requests.get(url)

        if res.status_code not in [200, 201]:
            my_logger.error("get_queue_list fail! - " + str(res.status_code))
            return None

        img = Image.open(BytesIO(res.content))
        img.save(save_file, img_format, quality=95)

    except TimeoutError:
        my_logger.error("image 수령 중 Timeout 발생!")
        traceback.print_exc()

    if not is_img(save_file, my_logger):
        my_logger.error("이미지 파일이 생성되지 않았습니다! - " + save_file)
        return False
    else:
        return True


def get_optimized_size(img_file: str, max_width: int, max_height: int, my_logger: Logger):
    """
    지정된 너비/높이까지 정방향으로 얼마나 늘어나야 하는지 비율 계산 및 계산된 w, h 리턴

    Parameters
    ----------
    img_file : str
        원본 이미지 객체의 파일명, 경로
    max_width : int
        최대 확장 가능한 너비
    max_height : int
        최대 확장 가능한 높이
    my_logger : Logger
        사용할 로깅 객체

    Returns
    -------
    list[int, int]
        [w, h] <- 최적화된 [너비, 높이]
    """
    if not is_img(img_file, my_logger):
        return False

    img = Image.open(img_file)
    ratio = 1.0
    origin_w, origin_h = img.size
    curr_w = origin_w * ratio
    curr_h = origin_h * ratio
    if curr_w > max_width or curr_h > max_height:
        while curr_w > max_width or curr_h > max_height:
            curr_w = origin_w * ratio
            curr_h = origin_h * ratio
            ratio -= 0.001

    else:
        while curr_w < max_width and curr_h < max_height:
            curr_w = origin_w * ratio
            curr_h = origin_h * ratio
            ratio += 0.001
    # 1클릭 차이로 조건에 안 맞아 튕겼으니 직전 조건으로 회귀 및 적용
    curr_w = int(origin_w * (ratio - 0.001))
    curr_h = int(origin_h * (ratio - 0.001))

    return curr_w, curr_h


def move_img(original_path: str, target_path: str, my_logger: Logger):
    """
    original_path 경로에 있는 pdf 파일/이미지 파일들을 target_path에 온전히 이미지 파일로만 적재

    Parameters
    ----------
    original_path : str
        Invoice 원본이 적재된 경로
    target_path : str
        pdf를 이미지로 변환하여 적재할 경로 (원본 이미지의 경우 그대로 복사하여 이 경로로 이동)
    my_logger : Logger
        사용할 로깅 객체

    Returns
    -------
    bool
        성공/실패
    """
    for filename in os.listdir(original_path):
        # 경로인지 파일인지 탐색 및 경로면 넘어가기
        if os.path.isdir(original_path + filename):
            my_logger.warning(filename + " 은/는 경로입니다.")
            continue
        # 만일 이미 format 된 거면 넘어가기
        if is_duplicated(filename, target_path):
            my_logger.warning("Already formatted : " + filename)
            continue

        # 파일 형식이 pdf면 pdf를 이미지로 변환
        if filename.lower().endswith('.pdf'):
            my_logger.info("PDF 이미지화: " + filename)
            if not pdf_to_img(original_path + filename, target_path, my_logger):
                return False
        # 이미지 형식이면 복사
        elif filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            shutil.copy(original_path + filename, target_path + filename)
        # 지정된 형식이 아닐 경우 넘어가기
        else:
            my_logger.error(filename + ': 지정되지 않은 형식. .pdf, .png, .jpg, .jpeg 가 아니면 안됩니다.')
            return False
    return True


def pdf_to_img(filename: str, save_dir: str, my_logger: Logger):
    """
    전달 받은 pdf 파일 내 장수 상관 없이 모두 이미지 파일로 변경

    Parameters
    ----------
    filename : str
        pdf 경로, 파일명
    save_dir : str
        이미지 변환 후 저장할 경로, 파일명
    my_logger : Logger
        사용할 로깅 객체

    Returns
    -------
    bool
        성공/실패
    """
    # 대상 pdf에서 확장자명 제외하고 이름만 추출
    base_filename = os.path.splitext(os.path.basename(filename))[0]
    processed_img_list = []
    try:
        # pdf 파일 내 각 장을 리스트로 변환
        pages = convert_from_path(filename)
        # 만약 한장이라면
        if len(pages) == 1:
            # 0번째 index를 가져옴 (한장이더라도 리스트로 반환하기 때문)
            img_name = os.path.join(save_dir, base_filename) + '.jpg'
            processed_img_list.append(img_name)
            pages[0].save(img_name, 'JPEG')
        else:
            # 여러장이면 각 장을 [0], [1] 순으로 파일 인덱싱을 새로 하여 저장
            page_count = 1
            for page in pages:
                img_name = os.path.join(save_dir, base_filename) + '(' + str(page_count) + ').jpg'
                processed_img_list.append(img_name)
                page.save(img_name, 'JPEG')
                page_count += 1

    except Exception as ex:
        my_logger.error("PDF 파일을 이미지로 변환하는데 실패했습니다: " + filename + " -> {}".format(ex))
        # 혹시 일부가 이미 이미지로 변환되었다면 해당 파일을 모두 지울 것
        for img in os.listdir(save_dir):
            if img in processed_img_list:
                os.remove(save_dir + img)
        return False
    return True
