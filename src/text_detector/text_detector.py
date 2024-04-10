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
    def __init__(self, input_size, model_path):
        self.input_size = input_size
        self.model = cv2.dnn.readNetFromONNX(model_path)
        self.uoln = self.model.getUnconnectedOutLayersNames()

    def __call__(self, im_in):
        blob = cv2.dnn.blobFromImage(
            im_in, scalefactor=1 / 255.0, size=(self.input_size, self.input_size)
        )
        self.model.setInput(blob)
        blocks, mask, lines_map = self.model.forward(self.uoln)
        return blocks, mask, lines_map


def preprocess_img(
    img, input_size=(1024, 1024), device="cpu", bgr2rgb=True, half=False, to_tensor=True
):
    if bgr2rgb:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_in, ratio, (dw, dh) = letterbox(
        img, new_shape=input_size, auto=False, stride=64
    )
    if to_tensor:
        img_in = img_in.transpose((2, 0, 1))[::-1]  # HWC to CHW, BGR to RGB
        img_in = (
            numpy.array([numpy.ascontiguousarray(img_in)]).astype(numpy.float32) / 255
        )
        if to_tensor:
            img_in = torch.from_numpy(img_in).to(device)
            if half:
                img_in = img_in.half()
    return img_in, ratio, int(dw), int(dh)


def postprocess_mask(img: Union[torch.Tensor, numpy.ndarray], thresh=None):
    # img = img.permute(1, 2, 0)
    if isinstance(img, torch.Tensor):
        img = img.squeeze_()
        if img.device != "cpu":
            img = img.detach_().cpu()
        img = img.numpy()
    else:
        img = img.squeeze()
    if thresh is not None:
        img = img > thresh
    img = img * 255
    # if isinstance(img, torch.Tensor):

    return img.astype(numpy.uint8)


def postprocess_yolo(det, conf_thresh, nms_thresh, resize_ratio, sort_func=None):
    det = non_max_suppression(det, conf_thresh, nms_thresh)[0]
    # bbox = det[..., 0:4]
    if det.device != "cpu":
        det = det.detach_().cpu().numpy()
    det[..., [0, 2]] = det[..., [0, 2]] * resize_ratio[0]
    det[..., [1, 3]] = det[..., [1, 3]] * resize_ratio[1]
    if sort_func is not None:
        det = sort_func(det)

    blines = det[..., 0:4].astype(numpy.int32)
    confs = numpy.round(det[..., 4], 3)
    cls = det[..., 5].astype(numpy.int32)
    return blines, cls, confs


class TextDetector:
    lang_list = ["eng", "ja", "unknown"]
    langcls2idx = {"eng": 0, "ja": 1, "unknown": 2}

    def __init__(
        self,
        model_path=r"text_detector/model/comictextdetector.onnx",
        input_size=1024,
        device="cpu",
        half=False,
        nms_thresh=0.35,
        conf_thresh=0.4,
        mask_thresh=0.3,
        act="leaky",
    ):
        super(TextDetector, self).__init__()
        self.model = cv2.dnn.readNetFromONNX(model_path)
        self.net = TextDetBaseDNN(input_size, model_path)
        self.backend = "opencv"

        if isinstance(input_size, int):
            input_size = (input_size, input_size)

        self.input_size = input_size
        self.device = device
        self.half = half
        self.conf_thresh = conf_thresh
        self.nms_thresh = nms_thresh
        self.seg_rep = SegDetectorRepresenter(thresh=0.3)

    def __call__(self, img, refine_mode=1, keep_undetected_mask=True):
        img_in, ratio, dw, dh = preprocess_img(
            img,
            input_size=self.input_size,
            device=self.device,
            half=self.half,
            to_tensor=self.backend == "torch",
        )
        im_h, im_w = img.shape[:2]

        blks, mask, lines_map = self.net(img_in)

        resize_ratio = (
            im_w / (self.input_size[0] - dw),
            im_h / (self.input_size[1] - dh),
        )
        blks = postprocess_yolo(blks, self.conf_thresh, self.nms_thresh, resize_ratio)

        if mask.shape[1] == 2:  # some version of opencv spit out reversed result
            tmp = mask
            mask = lines_map
            lines_map = tmp

        mask = postprocess_mask(mask)

        lines, scores = self.seg_rep(self.input_size, lines_map)
        box_thresh = 0.6
        idx = numpy.where(scores[0] > box_thresh)
        lines, scores = lines[0][idx], scores[0][idx]

        # map output to input img
        mask = mask[: mask.shape[0] - dh, : mask.shape[1] - dw]
        mask = cv2.resize(mask, (im_w, im_h), interpolation=cv2.INTER_LINEAR)
        if lines.size == 0:
            lines = []
        else:
            lines = lines.astype(numpy.float64)
            lines[..., 0] *= resize_ratio[0]
            lines[..., 1] *= resize_ratio[1]
            lines = lines.astype(numpy.int32)
        blk_list = group_output(blks, lines, im_w, im_h, mask)
        mask_refined = refine_mask(img, mask, blk_list, refine_mode=refine_mode)
        if keep_undetected_mask:
            mask_refined = refine_undetected_mask(
                img, mask, mask_refined, blk_list, refine_mode=refine_mode
            )

        return mask, mask_refined, blk_list
