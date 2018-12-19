#!/usr/bin/env python
# -*- coding:utf8 -*-

import numpy
import cv2
import dlib

predictor_path = "../static/shape_predictor_5_face_landmarks.dat"

def add_hat(head_img_path, hat_img_path):
    """return the path of head with hat
    """
    #处理图像，微信头像格式位jpg三通道
    head_img = cv2.imread(head_img_path)
    hat_img = cv2.imread(hat_img_path, -1)
    
    #分离rgba通道，合成rgb三通道帽子图，a通道后面做mask用
    r, g, b, a = cv2.split(hat_img) 
    rgb_hat = cv2.merge((r,g,b))

    #dlib人脸关键点检测器
    predictor = dlib.shape_predictor(predictor_path)  

    # dlib正脸检测器
    detector = dlib.get_frontal_face_detector()
    # 正脸检测
    dets = detector(head_img, 1)
    # 如果检测到人脸
    if len(dets)>0:  
        for d in dets:
            #人脸的左边、人脸的顶部、宽度、高度
            x,y,w,h = d.left(),d.top(), d.right()-d.left(), d.bottom()-d.top()
            
            # 关键点检测，5个关键点
            shape = predictor(head_img, d)
           
            # 选取左右眼眼角的点
            point1 = shape.part(0)
            point2 = shape.part(2)

            # 求两点中心
            eyes_center = ((point1.x+point2.x)//2,(point1.y+point2.y)//2)
    
            #  根据人脸大小调整帽子大小
            factor = 2.5
            resized_hat_h = int(round(rgb_hat.shape[0]*w/rgb_hat.shape[1]*factor))
            resized_hat_w = int(round(rgb_hat.shape[1]*w/rgb_hat.shape[1]*factor))
            if resized_hat_h > y:
                resized_hat_h = y
            resized_hat = cv2.resize(rgb_hat,(resized_hat_w,resized_hat_h))
            #print "根据人脸调整后的帽子size:", resized_hat_h, resized_hat_w

            # 帽子相对与人脸框上线的偏移量
            dh = 0
            dw = 0

            # 求帽子的所在区域，根据边框裁剪
            top = y + dh - resized_hat_h
            if top < 0:
                top = 0
            #print "top:", y + dh - resized_hat_h, top

            bottom = y + dh
            if bottom >= head_img.shape[0]:
                bottom = head_img.shape[0] - 1
            #print "bottom:", y + dh - 1, bottom
            
            left = eyes_center[0]-resized_hat_w/2
            if left < 0:
                left = 0
            #print "left:", eyes_center[0]-resized_hat_w/2, left
            
            right = eyes_center[0]+resized_hat_w/2
            if right >= head_img.shape[1]:
                right = head_img.shape[1] - 1
            #print "right:", eyes_center[0]+resized_hat_w/2, right

            bg_roi = head_img[top:bottom, left:right]
            #cv2.imwrite("bg.jpg", bg_roi)
            #print "bg:", top, bottom, left, right
            #bg_w = right - left
            #bg_h = bottom - top

            #修剪帽子
            cut_hat = resized_hat[top - (y + dh - resized_hat_h):bottom, (left - (eyes_center[0]-resized_hat_w/2)):(resized_hat_w - (right - (eyes_center[0]+resized_hat_w/2)))]
            #print top - (y + dh - resized_hat_h), bottom, (left - (eyes_center[0]-resized_hat_w/2)), (resized_hat_w - (right - (eyes_center[0]+resized_hat_w/2)))

            # 用alpha通道作为mask
            a = cv2.resize(a, (resized_hat_w,resized_hat_h))
            a = a[top - (y + dh - resized_hat_h):bottom, (left - (eyes_center[0]-resized_hat_w/2)):(resized_hat_w - (right - (eyes_center[0]+resized_hat_w/2)))]
            mask = cv2.resize(a, (cut_hat.shape[1] ,cut_hat.shape[0]))
            mask_inv =  cv2.bitwise_not(mask)

            # 原图ROI中提取放帽子的区域
            bg_roi = bg_roi.astype(float)
            mask_inv = cv2.merge((mask_inv,mask_inv,mask_inv))
            alpha = mask_inv.astype(float)/255

            # 相乘之前保证两者大小一致（可能会由于四舍五入原因不一致）
            alpha = cv2.resize(alpha, (bg_roi.shape[1],bg_roi.shape[0]))
            bg = cv2.multiply(alpha, bg_roi)
            bg = bg.astype('uint8')
            # cv2.imwrite("bg.jpg",bg)

            # 提取帽子区域
            hat = cv2.bitwise_and(cut_hat,cut_hat,mask = mask)
            # cv2.imwrite("hat.jpg",hat)

            # 相加之前保证两者大小一致（可能会由于四舍五入原因不一致）
            hat = cv2.resize(hat,(bg_roi.shape[1],bg_roi.shape[0]))
            # 两个ROI区域相加
            add_hat = cv2.add(bg, hat)
            cv2.imwrite("merge_hat.jpg", add_hat)

            # 把添加好帽子的区域放回原图
            head_img[top:bottom, left:right] = add_hat
    else:
        return None
    head_with_hat_img_path = head_img_path.replace('.jpg', '') + '_with_hat.jpg'
    cv2.imwrite(head_with_hat_img_path, head_img)
    return head_with_hat_img_path


if __name__ == "__main__":
    import sys
    print "python hat.py head_image hat_image..."
    print sys.argv[1], sys.argv[2]
    print add_hat(sys.argv[1], sys.argv[2])
