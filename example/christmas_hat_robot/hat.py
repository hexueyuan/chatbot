# -*- coding:utf8 -*-

#import hat
import numpy
import json
import dlib
import cv2
import math

predictor_path = "static/shape_predictor_5_face_landmarks.dat"

#将图片沿着图片中点逆时针旋转
def rotate(image, angle, center=None, scale=1.0): #1
    (h, w) = image.shape[:2] #2
    if center is None: #3
        center = (w // 2, h // 2) #4

    M = cv2.getRotationMatrix2D(center, angle, scale) #5

    rotated = cv2.warpAffine(image, M, (w, h)) #6
    return rotated #7

# 求p2 -> p1与y正半轴的夹角弧度制
def offset_angle(point1, point2):
    len = math.sqrt((point1[0] - point2[0]) * (point1[0] - point2[0]) + (point1[1] - point2[1]) * (point1[1] - point2[1]))
    theta = math.acos((point1[1] - point2[1]) / len)
    return theta

def add_hat(head_img_path, hat_img_path):
    head_img = cv2.imread(head_img_path)
    hat_img = cv2.imread(hat_img_path, -1)

    #加载人脸识别训练模型，检测图片中的人脸图像
    predictor = dlib.shape_predictor(predictor_path)  
    detector = dlib.get_frontal_face_detector()
    dets = detector(head_img, 1)

    if len(dets) > 0:
        head_img = add_hat_to_face(head_img, hat_img, predictor, dets)
        head_with_hat_img_path = head_img_path.replace('.jpg', '') + '_with_hat.jpg'
        cv2.imwrite(head_with_hat_img_path, head_img)
        return head_with_hat_img_path
    else:
        return None

def add_hat_to_face(head_img, hat_img, predictor, dets):
    """return the path of head with hat
    """
    for d in dets:
        # 关键点检测，5个关键
        shape = predictor(head_img, d)

        # 计算帽子随人脸的偏转角度
        # 右眼的中点
        mid1 = ((shape.part(0).x + shape.part(1).x) / 2, (shape.part(0).y + shape.part(1).y) / 2)
        # 左眼的中点
        mid2 = ((shape.part(2).x + shape.part(3).x) / 2, (shape.part(2).y + shape.part(3).y) / 2)
        theta = offset_angle(mid2, mid1)
        real_angle = int((math.pi * 2.5 - theta) * 180 / math.pi)
        ex_hat = rotate(hat_img, real_angle)

        # 根据人脸大小调整帽子大小, 人脸大小由双眼眼角距离决定
        leye = shape.part(0)
        reye = shape.part(2)
        eye_distance = math.sqrt((leye.x - reye.x) * (leye.x - reye.x) + (leye.y - reye.y) * (leye.y - reye.y))
        # k1参数表示帽子图片相对人脸的大小
        k1 = 2.3 * 3
        face_width = eye_distance
        resized_hat_w = int(face_width * k1)
        resized_hat_h = int(hat_img.shape[0] * resized_hat_w / hat_img.shape[1])
        resized_hat = cv2.resize(ex_hat,(resized_hat_w,resized_hat_h))

        # 求解帽子相对人脸的垂直偏移
        # 系数k2表示帽子到双眼所在水平线的距离为双眼所在水平线到门中的距离的k倍
        k2 = 1.3

        #门中到双眼线的距离, 这里简化为求门中到双眼中点的距离
        mid_eye = ((mid1[0] + mid2[0]) / 2, (mid1[1] + mid2[1]) / 2)
        point_nose = shape.part(4)
        distance = math.sqrt((mid_eye[0] - point_nose.x) * (mid_eye[0] - point_nose.x) + (mid_eye[1] - point_nose.y) * (mid_eye[1] - point_nose.y))

        # 求帽子在头像图片中的位置
        angle_offset = math.pi - theta
        img_bottom = int((d.top() + (resized_hat.shape[0] / 2) - (k2 * distance * math.sin(angle_offset) - (mid_eye[1] - d.top()))))
        img_top = int(img_bottom - resized_hat.shape[0])
        img_left = int(k2 * distance * math.cos(angle_offset) + mid_eye[0] - 0.5 * resized_hat.shape[1])
        img_right = int(img_left + resized_hat.shape[1])
        #裁剪图片
        if img_left < 0:
            delta_left = 0 - img_left
            img_left = 0
        else:
            delta_left = 0
        if img_right > head_img.shape[1]:
            delta_right = img_right - head_img.shape[1]
            img_right = head_img.shape[1] - 1
        else:
            delta_right = 0
        if img_top < 0:
            deleta_top = 0 - img_top
            img_top = 0
        else:
            deleta_top = 0
        #默认bottom不会超过头像图片
        bg_roi = head_img[img_top:img_bottom, img_left:img_right]
        hat_roi = resized_hat[deleta_top:resized_hat.shape[0], delta_left:resized_hat.shape[1] - delta_right]
        r, g, b, a = cv2.split(hat_roi)
        rgb_hat_roi = cv2.merge((r, g, b))

        mask_inv =  cv2.bitwise_not(a)

        ## 原图ROI中提取放帽子的区域
        bg_roi = bg_roi.astype(float)
        mask_inv = cv2.merge((mask_inv,mask_inv,mask_inv))
        alpha = mask_inv.astype(float)/255

        ## 相乘之前保证两者大小一致（可能会由于四舍五入原因不一致）
        alpha = cv2.resize(alpha, (bg_roi.shape[1],bg_roi.shape[0]))
        bg = cv2.multiply(alpha, bg_roi)
        bg = bg.astype('uint8')
        ## cv2.imwrite("bg.jpg",bg)

        ## 提取帽子区域
        hat = cv2.bitwise_and(rgb_hat_roi, rgb_hat_roi, mask = a)
        ## cv2.imwrite("hat.jpg",hat)

        ## 相加之前保证两者大小一致（可能会由于四舍五入原因不一致）
        hat = cv2.resize(hat,(bg_roi.shape[1],bg_roi.shape[0]))
        ## 两个ROI区域相加
        add_hat = cv2.add(bg, hat)

        ## 把添加好帽子的区域放回原图
        head_img[img_top:img_bottom, img_left:img_right] = add_hat
    return head_img
