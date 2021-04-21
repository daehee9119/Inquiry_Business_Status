# 표준 라이브러리
import os
import io
import shutil
from logging import Logger
# 3rd party
import psutil
from ctypes import windll
# 내부 패키지


def is_locked(filepath: str, my_logger: Logger):
    """
    전달 받은 파일이 다른 사용자에 의해 쓰이고 있는지 확인. 로그 파일의 원활한 사용을 위해 맨 처음 잡아준다.
    TimeRotating 사용 시 전날로 로그를 복사하면서 해당 핸들러가 물고 안 놔줄 수 있기 때문

    Parameters
    ----------
    filepath : str
        생성할 dir 리스트, 1개일 경우도 리스트 1개짜리로 만들어서 넣어줘야 함
    my_logger : Logger
        사용할 로깅 객체

    Returns
    -------
    bool
        제3자가 파일 사용 중인지 여부
    """
    locked = None
    file_object = None
    if os.path.exists(filepath):
        try:
            my_logger.info("Trying to open - " + filepath)
            buffer_size = 8
            file_object = io.open(filepath, 'a', buffer_size, encoding='utf-8')
            if file_object:
                my_logger.info(filepath + " is not locked.")
                locked = False
        except IOError as e:
            my_logger.error("File is locked (unable to open in append mode). " + e)
            locked = True
        finally:
            if file_object:
                file_object.close()
                my_logger.info(filepath + " closed")
    else:
        my_logger.info(filepath + " is not found")

    # for i in range(0, 10):
    #     try:
    #         f = io.open(abs_path + log_dict['file_name'], 'rt', encoding='utf-8')
    #         lines = f.readlines()
    #         f.close()
    #         if "case_" + initiate_code + "_result:" in lines[:-1]:
    #             break
    #     except IOError as e:
    #         logger.info("다른 사용자가 로그 파일 사용 중! - " + e)
    #         time.sleep(0.5)

    return locked


def kill_process(target_pid: int):
    """
    지정된 process id 기반 프로세스 kill

    Parameters
    ----------
    target_pid : int
        제거 대상 프로세스의 pid

    Returns
    -------
    bool
        프로세스 제거 여부
    """
    is_success = False
    try:
        parent = psutil.Process(target_pid)
        for child in parent.children(recursive=True):
            child.kill()
        parent.kill()
        is_success = True
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        pass
    return is_success


def is_task_exist(p_name: str, my_logger: Logger):
    """
    특정 태스크가 존재하는지, 존재하면 pid 리턴

    Parameters
    ----------
    p_name : str
        프로세스 이름 (실행파일명 혹은 이름)
    my_logger : Logger
        사용할 로깅 객체

    Returns
    -------
    int
        탐색된 프로세스의 pid
    """
    pid = -1
    # 프로세스 리스트를 순회하면서 sap 프로세스가 수행되는지 여부 확인
    for process in psutil.process_iter():
        try:
            if p_name == process.name():
                pid = process.pid
                break
        except (psutil.PermissionError, psutil.AccessDenied):
            my_logger.warning("Permission error has been occurred")
            continue
    return pid


def make_dir(dir_list: list, my_logger: Logger):
    """
    경로 리스트를 배열로 받아 모두 만들어 줌. 없을때만 만들고 있으면 넘어감

    Parameters
    ----------
    dir_list : list
        생성할 dir 리스트, 1개일 경우도 리스트 1개짜리로 만들어서 넣어줘야 함
    my_logger : Logger
        사용할 로깅 객체

    Returns
    -------
    bool
        경로 생성 여부
    """
    for target_dir in dir_list:
        try:
            if not(os.path.isdir(target_dir)):
                os.makedirs(os.path.join(target_dir))
        except OSError as ex:
            my_logger.error("Failed to create Dir! => " + target_dir + '\n' + str(ex))
            return False
    return True


def remove_dir(target_dir: str, my_logger: Logger):
    """
    디렉토리가 존재하는 경우 해당 디렉토리 삭제
    그냥 해도 되긴 하는데..try catch 처리를 위해 따로 구현

    Parameters
    ----------
    target_dir : str
        삭제할 디렉토리, abs나 rel 상관 없음
    my_logger : Logger
        사용할 로깅 객체

    Returns
    -------
    bool
        삭제 여부
    """
    try:
        if os.path.isdir(target_dir):
            # rmtree를 써야 디렉토리 안에 파일까지 깔끔하게 날아감
            shutil.rmtree(target_dir)
    except OSError as ex:
        my_logger.error("Failed to remove Dir! => " + target_dir + '\n' + str(ex))
        return False
    return True


def is_duplicated(target_name: str, src_path: str):
    """
    특정 파일이 다른 경로 내 파일 리스트 이름에 포함되는지 확인

    Parameters
    ----------
    target_name : str
        확인할 파일명
    src_path : str
        대조할 파일 리스트 경로

    Returns
    -------
    bool
        경로 내 파일 존재 여부
    """
    # 확장자, 경로 제외한 순수 파일명
    base_filename = os.path.splitext(os.path.basename(target_name))[0]
    # 원본 경로를 순회하면서 base_filename 이 src_item 에 포함되는지 확인
    for src_item in os.listdir(src_path):
        if base_filename in src_item:
            return True
    # 확인한 boolean 리턴
    return False


def is_file_type(target_file: str, file_type: str, my_logger: Logger):
    """
    파일 형태인지, 특정 확장자를 가지고 있는지 검증

    Parameters
    ----------
    target_file : str
        검증할 파일명
    file_type : str
        검증할 file extension (png, xlsx, etc)
    my_logger : Logger
        사용할 로깅 객체

    Returns
    -------
    bool
        해당 file extension 으로 끝나는지 여부
    """
    if not os.path.isfile(target_file):
        my_logger.error("파일이 존재하지 않습니다! - " + target_file)
        return False
    # 검증할 확장자명
    if target_file.lower().endswith(file_type):
        return True
    return False


def get_path(target_file: str, my_logger: Logger):
    """
    파일의 디렉토리만 반환

    Parameters
    ----------
    target_file : str
        디렉토리 추출할 파일
    my_logger : Logger
        사용할 로깅 객체

    Returns
    -------
    str
        해당 파일의 경로만 반환
    """
    if not os.path.isfile(target_file):
        my_logger.error("파일이 존재하지 않습니다! - " + target_file)
        return None
    ret_dir = os.path.splitext(os.path.dirname(target_file))[0]
    return ret_dir


def get_embedded_directory(target_dir: str, my_logger: Logger):
    """
    경로 내 폴더 리스트만 반환

    Parameters
    ----------
    target_dir : str
        서브 폴더를 담고 있는 루트 경로
    my_logger : Logger
        사용할 로깅 객체

    Returns
    -------
    list
        탐색한 모든 서브 폴더 리스트
    """
    if not os.path.isdir(target_dir):
        my_logger.error("경로가 존재하지 않습니다! - " + target_dir)
        return None
    dir_list = [name for name in os.listdir(target_dir) if os.path.isdir(os.path.join(target_dir, name))]
    return dir_list


def get_valid_file_name(target_file: str):
    """
    주어진 문자열에서 파일명에 사용 불가한 문자 제거

    Parameters
    ----------
    target_file : str
        특수문자 제거할 파일명

    Returns
    -------
    str
        특수문자 제거된 파일명
    """
    invalid_char = ['\\', '/', ':', '*', '?', '<', '>', '|']

    for char in invalid_char:
        target_file = target_file.replace(char, "")

    return target_file


def clear_clipboard():
    """
    클립보드를 비우는 함수
    Deprecated

    Returns
    -------
    bool
        클리어 여부
    """
    try:
        if windll.user32.OpenClipboard(None):
            windll.user32.EmptyClipboard()
            windll.user32.CloseClipboard()
    except Exception as e:
        print(e)
        return False
    return True
