import os
import shutil
import traceback


def make_dir(dir_list):
    """
    경로가 없을때만 만들고, 있으면 넘어감.
    :param dir_list:
    :return:
    """
    for target_dir in dir_list:
        try:
            if not(os.path.isdir(target_dir)):
                os.makedirs(os.path.join(target_dir))
        except OSError as ex:
            print("Failed to create Dir! = ", target_dir, "\n", ex)
            traceback.print_stack()
            traceback.print_exc()
        finally:
            continue


def remove_dir(target_dir):
    """
    디렉토리가 존재하는 경우에만 해당 디렉토리 삭제
    이거도 예외 처리 포함해서 놔야 할 것 같아서 따로 빼둠
    :param target_dir:
    :return: None
    """
    try:
        if os.path.isdir(target_dir):
            shutil.rmtree(target_dir)
    except OSError as ex:
        print("Failed to remove Dir! = ", target_dir, "\n", ex)
        traceback.print_stack()
        traceback.print_exc()
