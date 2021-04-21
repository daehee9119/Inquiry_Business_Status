# 표준 라이브러리
import io
# 3rd party
# 내부 패키지


def detect_img_text(path: str):
    """
    수령한 이미지를 vision api를 사용해 텍스트로 변환한 후 해당 텍스트 반환

    Parameters
    ----------
    path : str
        이미지 경로명, 파일명

    Returns
    -------
    str
        이미지에서 추출한 full string
    """

    """Detects text in the file."""
    from google.cloud import vision

    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))
    else:
        return_text = texts[0].description
        return return_text
