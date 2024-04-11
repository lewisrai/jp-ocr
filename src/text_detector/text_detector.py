import cv2
import numpy
import torch

from typing import Union

from .utils.db_utils import SegDetectorRepresenter
from .utils.imgproc_utils import letterbox
from .utils.textblock import group_output
from .utils.textmask import (
    refine_mask,
    refine_undetected_mask,
)
from .utils.yolov5_utils import non_max_suppression


class TextDetBaseDNN:
    def __init__(self, model_path, input_size):
        self.input_size = input_size
        self.model = cv2.dnn.readNetFromONNX(model_path)
        self.uoln = self.model.getUnconnectedOutLayersNames()

    def __call__(self, image):
        blob = cv2.dnn.blobFromImage(
            image, scalefactor=1 / 255.0, size=(self.input_size, self.input_size)
        )

        self.model.setInput(blob)
        blocks, mask, lines_map = self.model.forward(self.uoln)

        return blocks, mask, lines_map


def preprocess_image(image, input_size=(1024, 1024)):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image, ratio, (dw, dh) = letterbox(
        image, new_shape=input_size, auto=False, stride=64
    )

    return image, ratio, int(dw), int(dh)


def postprocess_mask(image: Union[torch.Tensor, numpy.ndarray]):
    image = image.squeeze()
    image = image * 255

    return image.astype(numpy.uint8)


def postprocess_yolo(det, resize_ratio, conf_thresh=0.4, nms_thresh=0.35):
    det = non_max_suppression(det, conf_thresh, nms_thresh)[0]
    det = det.detach_().cpu().numpy()
    det[..., [0, 2]] = det[..., [0, 2]] * resize_ratio[0]
    det[..., [1, 3]] = det[..., [1, 3]] * resize_ratio[1]

    blines = det[..., 0:4].astype(numpy.int32)
    confs = numpy.round(det[..., 4], 3)
    cls = det[..., 5].astype(numpy.int32)

    return blines, cls, confs


class TextDetector:
    def __init__(
        self,
        model_path=r"text_detector/model/comictextdetector.onnx",
        input_size=1024,
    ):
        self.model = cv2.dnn.readNetFromONNX(model_path)
        self.net = TextDetBaseDNN(model_path, input_size)
        self.backend = "opencv"

        self.input_size = (input_size, input_size)
        self.device = "cpu"
        self.seg_rep = SegDetectorRepresenter(thresh=0.3)

    def __call__(self, image, refine_mode=1):
        image_height, image_width, _ = image.shape

        image_temp, ratio, dw, dh = preprocess_image(
            image,
        )

        blocks, mask, lines_map = self.net(image_temp)

        resize_ratio = (
            image_width / (self.input_size[0] - dw),
            image_height / (self.input_size[1] - dh),
        )

        blocks = postprocess_yolo(blocks, resize_ratio)

        if mask.shape[1] == 2:
            tmp = mask
            mask = lines_map
            lines_map = tmp

        mask = postprocess_mask(mask)

        lines, scores = self.seg_rep(self.input_size, lines_map)
        index = numpy.where(scores[0] > 0.6)
        lines, scores = lines[0][index], scores[0][index]

        mask = mask[: mask.shape[0] - dh, : mask.shape[1] - dw]
        mask = cv2.resize(
            mask, (image_width, image_height), interpolation=cv2.INTER_LINEAR
        )

        if lines.size == 0:
            lines = []
        else:
            lines = lines.astype(numpy.float64)
            lines[..., 0] *= resize_ratio[0]
            lines[..., 1] *= resize_ratio[1]
            lines = lines.astype(numpy.int32)

        block_list = group_output(blocks, lines, image_width, image_height, mask)
        mask_refined = refine_mask(image, mask, block_list, refine_mode=refine_mode)

        mask_refined = refine_undetected_mask(
            image, mask, mask_refined, block_list, refine_mode=refine_mode
        )

        return mask, mask_refined, block_list
