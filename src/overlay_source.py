import base64
import cv2
import numpy

from io import BytesIO
from manga_ocr.manga_ocr import MangaOcr
from PIL import Image
from scipy.signal.windows import gaussian
from text_detector.text_detector import TextDetector


class OverlaySource:
    def __init__(self):
        self.manga_ocr = MangaOcr()
        self.text_detector = TextDetector()

    def __call__(self, image_base64):
        image = Image.open(BytesIO(base64.b64decode(image_base64)))
        image = numpy.array(image)
        image = image[:, :, ::-1].copy()

        mask, mask_refined, block_list = self.text_detector(image)

        results = []

        for block_index, block in enumerate(block_list):
            result_block = {
                "box": list(map(int, list(block.xyxy))),
                "vertical": bool(block.vertical),
                "font_size": block.font_size,
                "lines_coords": [],
                "lines": [],
            }

            for line_index, line in enumerate(block.lines_array()):
                if block.vertical:
                    max_ratio = 16
                else:
                    max_ratio = 8

                line_crops, cut_points = split_into_chunks(
                    image,
                    mask_refined,
                    block,
                    line_index,
                    max_ratio,
                )

                line_text = ""

                for line_crop in line_crops:
                    if block.vertical:
                        line_crop = cv2.rotate(line_crop, cv2.ROTATE_90_CLOCKWISE)

                    line_text += self.manga_ocr(Image.fromarray(line_crop))

                result_block["lines_coords"].append(line.tolist())
                result_block["lines"].append(line_text)

            results.append(result_block)

        return results


def split_into_chunks(
    image, mask_refined, block, line_index, max_ratio, textheight=64, anchor_window=2
):
    line_crop = block.get_transformed_region(image, line_index, textheight)
    height, width, _ = line_crop.shape

    ratio = width / height

    if ratio <= max_ratio:
        return [line_crop], []

    k = gaussian(textheight * 2, textheight / 8)

    line_mask = block.get_transformed_region(mask_refined, line_index, textheight)
    num_chunks = int(numpy.ceil(ratio / max_ratio))

    anchors = numpy.linspace(0, width, num_chunks + 1)[1:-1]

    line_density = line_mask.sum(axis=0)
    line_density = numpy.convolve(line_density, k, "same")
    line_density /= line_density.max()

    anchor_window *= textheight

    cut_points = []

    for anchor in anchors:
        anchor = int(anchor)

        n0 = numpy.clip(anchor - anchor_window // 2, 0, width)
        n1 = numpy.clip(anchor + anchor_window // 2, 0, width)

        p = line_density[n0:n1].argmin()
        p += n0

        cut_points.append(p)

    return numpy.split(line_crop, cut_points, axis=1), cut_points
