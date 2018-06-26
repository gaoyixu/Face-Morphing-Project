"""An little example using face morphing.

Author: Yixu Gao 15307130376"""
from face_morphing import FaceMorphing
from matplotlib import pyplot as plt


fm = FaceMorphing()
fm.set_src_path('zxh.jpg')
fm.set_dst_path('hzj.jpg')
fm.mode = 'RGB'
src_points = fm.auto_select_points('zxh.jpg')
dst_points = fm.auto_select_points('hzj.jpg')
src_img = fm.open_src_img()
dst_img = fm.open_dst_img()
dst_src_points_dict = fm.set_points(src_points, dst_points)
fm.mode = 'RGB'
print(dst_src_points_dict)
new_img = fm.advanced_morphing()
des_p = []
src_p = []

plt.subplot(1, 3, 1)
plt.imshow(fm.src_img)

plt.subplot(1, 3, 2)
plt.imshow(fm.dst_img)

plt.subplot(1, 3, 3)
plt.imshow(new_img)
plt.show()
