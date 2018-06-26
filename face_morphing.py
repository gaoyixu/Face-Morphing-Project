"""Face Morphing between Two Pictures.

Author:
    Yixu Gao 15307130376

Usage:
    Simple example:
        fm = FaceMorphing()
        fm.set_src_path('zxh-ape.jpg')
        fm.set_dst_path('ape.jpg')
        src_img = fm.open_src_img()
        dst_img = fm.open_dst_img()
        fm.set_points(zxh_points, ape_points)
        new_img = fm.morphing() (or fm.advanced_morphing())
        # And then you can show the three image:
        #   src_img, dst_img, new_img

    Parameter settings:
        Set fm.mode to choose either gray or rgb mode
        Set fm.distance_mode to choose either Euler or Manhattan distance
        Set fm.flag to determine only-face morphing or whole image morphing
        Remember: set the mode before morphing or it will use default.
        If face++ cannot work well,
            you can also change the id and password of Face++ API
                in auto_select_points settings
"""
import base64
import json
import os
import sys
from cv2 import Subdiv2D
import numpy as np

from PIL import Image

from urllib.error import URLError

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode
try:
    from urllib import urlopen
except ImportError:
    from urllib.request import urlopen


class FaceMorphing:
    """Face Morphing.

    You can run default_run() method to see how it works briefly.
    """

    def __init__(self):
        self._src_img_path = ''
        self._dst_img_path = ''
        self.src_img = None
        self.dst_img = None
        self.src_points = []
        self.dst_points = []
        self.dst_src_points_dict = {}
        self.distance_mode = 'Euler'
        self.mode = 'gray'
        self.result_x = 2000
        self.result_y = 2000
        self.flag = True

    def set_src_path(self, file_path):
        """Set the source file path.

        Args:
            file_path: a string, e.g. 'zxh-ape.jpg'
        """
        self._src_img_path = file_path

    def set_dst_path(self, file_path):
        """Set the destination file path.

        Args:
            file_path: a string, e.g. 'ape.jpg'
        """
        self._dst_img_path = file_path

    def open_src_img(self):
        """Open the source image file.

        Returns:
            An Image object contains source image information
        """
        if not os.path.exists(self._src_img_path):
            print('You should first set the source file path!')
            return False
        else:
            self.src_img = Image.open(self._src_img_path)
            return self.src_img

    def open_dst_img(self):
        """Open the destination image file.

        Returns:
            An Image object contains destination image information
        """
        if not os.path.exists(self._dst_img_path):
            print('You should first set the destination file path!')
            return False
        else:
            self.dst_img = Image.open(self._dst_img_path)
            return self.dst_img

    @staticmethod
    def auto_select_points(file_path,
                           key='GAETcWh6-EV3PJmDXUAL2m0MeBFzIY_u',
                           secret='3Ryqmrgziz7fwgdQUUmSVhDnAU3sLI9x',
                           url='https://api-cn.faceplusplus.com/facepp/v3/detect'):
        """Auto select points of both faces.

        Args:
            file_path: the image to be auto selected points
            key: string, API key of face++ detect
            secret: string, API secret of face++ detect
            url: API url of face++ detect

        Returns:
            selected points or False
        """
        if not os.path.exists(file_path):
            print('You should first set legal file path!')
            return False
        with open(file_path, 'rb') as fd:
            b64str = base64.b64encode(fd.read())
        para = {'api_key': key,
                'api_secret': secret,
                'image_base64': b64str,
                'return_landmark': 2}
        data = urlencode(para).encode('utf-8')
        try:
            request = urlopen(url, data)
            face_data = json.loads(request.read())
            faces = face_data['faces']
            if faces:
                land_marks = faces[0]['landmark']
                return {location: (land_marks[location]['x'],
                                   land_marks[location]['y'])
                        for location in land_marks}
            else:
                return False
        except URLError:
            return False

    def set_points(self, src_points, dst_points):
        """Set the special points to map.

        Returns:
            Dictionary mapping destination points to source points
            i.e.
                {<dst_point>: <src_point>}
        """
        if type(src_points) != type(dst_points):
            print('The data type of the points sets must be the same!')
            return
        if isinstance(src_points, dict):
            for key in src_points:
                if key in dst_points:
                    self.src_points.append(src_points[key])
                    self.dst_points.append(dst_points[key])
                    self.dst_src_points_dict[dst_points[key]] = src_points[key]
        elif isinstance(src_points, list):
            self.src_points = src_points
            self.dst_points = dst_points
            self.dst_src_points_dict = {dst_points[i]: src_points[i]
                                        for i in range(len(src_points))}
        else:
            print('The data type of the points sets must be both list or dict!')
            return
        return self.dst_src_points_dict

    @staticmethod
    def _build_distance_map(array):
        """Calculate the distance first to save time.

        Args:
            array: all size of points

        Returns:
            The square distance between the two points.
                i.e. {(i, j): i ** 2 + j ** 2}
        """
        x, y = array.shape
        square_map = [i * i for i in range(max(x, y) + 1)]
        distance_map = {}
        for i in range(max([x, y])):
            for j in range(max([x, y])):
                distance_map[(i, j)] = square_map[i] + square_map[j]
        return distance_map

    @staticmethod
    def _build_distance_reverse_map(distance_map):
        """Calculate the reverse distance first to save time.

        Args:
            distance_map: square distance
                i.e. {(i, j): i ** 2 + j ** 2}

        Returns:
            The reverse distance between the two points."""
        distance_reverse_map = {
            (i, j): 1 / distance_map[(i, j)]
            if distance_map[(i, j)] != 0 else 1
            for i, j in distance_map}
        return distance_reverse_map

    def _distance_reverse(self, x0, y0, distance_map=None):
        """Get the reverse distance between two points.

        Args:
            x0: a tuple that contains coordinate
            y0: a tuple that contains coordinate
            distance_map: distance_map: square distance reverse

        Returns:
            The distance between the two points.

        You can change *distance_mode* to change the distance type.
        """
        if distance_map is None:
            distance_map = {}
        if self.distance_mode == 'Euler':
            if not distance_map:
                return 1 / (x0[0] - y0[0]) ** 2 + (x0[1] - y0[1]) ** 2
            else:
                return distance_map[(abs(x0[0] - y0[0]), abs(x0[1] - y0[1]))]
        else:
            return 1 / (float(abs((x0[0] - y0[0])) + abs(x0[1] - y0[1]))) ** 2

    def _distance(self, x0, y0, distance_map=None):
        """Calculate the distance between two points.

        Args:
            x0: a tuple that contains coordinate
            y0: a tuple that contains coordinate
            distance_map:

        Returns:
            The distance between the two points.

        You can change *distance_mode* to change the distance type.
        """
        if distance_map is None:
            distance_map = {}
        if self.distance_mode == 'Euler':
            if not distance_map:
                return (x0[0] - y0[0]) ** 2 + (x0[1] - y0[1]) ** 2
            else:
                return distance_map[(abs(x0[0] - y0[0]), abs(x0[1] - y0[1]))]
        else:
            return (float(abs((x0[0] - y0[0])) + abs(x0[1] - y0[1]))) ** 2

    @staticmethod
    def _interpolation(coordinate, img):
        """Interpolation.

        Args:
            coordinate: (x, y), x, y can be float
            img: np.array, 2 dimension

        Returns:
            Final value after interpolation
        """
        height, width = img.shape
        i, j = int(coordinate[0]), int(coordinate[1])
        u, v = coordinate[0] - i, coordinate[1] - j
        if j > height - 2:
            j = height - 2
        if i > width - 2:
            i = width - 2
        return ((1 - u) * (1 - v) * img[j][i]
                + (1 - u) * v * img[j][i + 1]
                + u * (1 - v) * img[j + 1][i]
                + u * v * img[j + 1][i + 1])

    @staticmethod
    def _find_bar(points_dict):
        """Find the smallest rectangle that all points in.

        Args:
            points_dict: {(i, j): (x, y)}
                (i, j) from dst, (x, y) from src

        Returns:
            [dst_left, dst_right, dst_up, dst_down,
                src_left, src_right, src_up, src_down]
        """
        dst_left, dst_right, dst_up, dst_down = sys.maxsize, -1, sys.maxsize, -1
        src_left, src_right, src_up, src_down = sys.maxsize, -1, sys.maxsize, -1
        for dst_i, dst_j in points_dict:
            src_i, src_j = points_dict[(dst_i, dst_j)]
            if dst_i < dst_left:
                dst_left = dst_i
            if dst_i > dst_right:
                dst_right = dst_i
            if dst_j < dst_up:
                dst_up = dst_j
            if dst_j > dst_down:
                dst_down = dst_j
            if src_i < src_left:
                src_left = src_i
            if src_i > src_right:
                src_right = src_i
            if src_j < src_up:
                src_up = src_j
            if src_j > src_down:
                src_down = src_j
        return [dst_left, dst_right, dst_up, dst_down,
                src_left, src_right, src_up, src_down]

    @staticmethod
    def _check_in_bar(bar_list, point):
        """Check whether the point is in the bar list.

        Args:
            point: x, y
            bar_list: [dst_left, dst_right, dst_up, dst_down,
                src_left, src_right, src_up, src_down]

        Returns:
            'in', 'near', or 'out'
        """
        x, y = point
        [dst_left, dst_right, dst_up, dst_down] = bar_list
        dst_width = dst_right - dst_left
        dst_height = dst_down - dst_up
        if dst_left < x < dst_right and dst_up < y < dst_down:
            return 'in'
        elif (dst_left - 0.1 * dst_width < x < dst_right + 0.1 * dst_width
              and dst_up - 0.1 * dst_height < y < dst_down + 0.1 * dst_height):
            return 'near'
        else:
            return 'out'

    def morphing(self):
        """Morphing from source image to destination image.

        You can choose mode 'gray' or 'RGB' by setting mode.


        Note that x, y = PLI.Image().size
            However, np.array((x, y)), which means the image is stored
                by column in array
        Return:
            New image object
        """
        if self.dst_img.size[0] > self.result_x \
                or self.dst_img.size[1] > self.result_y:
            rate = min([self.result_x / self.dst_img.size[0],
                        self.result_y / self.dst_img.size[1]])
            self.dst_img = self.dst_img.resize((
                int(rate * self.dst_img.size[0]) - 1,
                int(rate * self.dst_img.size[1]) - 1))
            new_dict = {
                (int(i * rate), int(j * rate)):
                    self.dst_src_points_dict[(i, j)]
                for (i, j) in self.dst_src_points_dict}
            self.dst_src_points_dict = new_dict
        if self.src_img.size[0] < self.dst_img.size[0]\
                or self.src_img.size[0] < self.dst_img.size[1]:
            rate = max([self.dst_img.size[0] / self.src_img.size[1],
                        self.dst_img.size[1] / self.src_img.size[0]])
            self.src_img = self.src_img.resize((
                int(rate * self.src_img.size[0]) + 1,
                int(rate * self.src_img.size[1]) + 1))
            new_dict = {
                (i, j):
                    (int(self.dst_src_points_dict[(i, j)][0] * rate),
                     int(self.dst_src_points_dict[(i, j)][1] * rate))
                for (i, j) in self.dst_src_points_dict}
            self.dst_src_points_dict = new_dict
        bar_list = self._find_bar(self.dst_src_points_dict)
        if self.mode == 'gray':
            src_gray = np.array(self.src_img.convert('L'))
            dst_gray = np.array(self.dst_img.convert('L'))
            dst_x, dst_y = dst_gray.shape
            morphing_img = np.zeros((dst_x, dst_y), dtype='float')
            dist_map = self._build_distance_map(dst_gray)
            dist_re_map = self._build_distance_reverse_map(dist_map)
            for j in range(dst_y):
                for i in range(dst_x):
                    position_state = self._check_in_bar(bar_list[:4], (i, j))
                    if (i, j) in self.dst_src_points_dict:
                        t_x, t_y = self.dst_src_points_dict[(i, j)]
                        morphing_img[j][i] = src_gray[t_y][t_x]
                    elif position_state == 'in':
                        total_distance = 0
                        t_x = 0
                        t_y = 0
                        for x, y in self.dst_src_points_dict:
                            src_x, src_y = self.dst_src_points_dict[(x, y)]
                            reverse_distance = self._distance_reverse(
                                (i, j), (x, y), dist_re_map)
                            total_distance += reverse_distance
                            t_x += (src_x - x + i) * reverse_distance
                            t_y += (src_y - y + j) * reverse_distance
                        t_x /= total_distance
                        t_y /= total_distance
                        if self._check_in_bar(bar_list[4:], (int(t_y), int(t_x))) == 'in':
                            morphing_img[j][i] = self._interpolation((t_x, t_y), src_gray)
                        else:
                            morphing_img[j][i] = dst_gray[j][i]
                    else:
                        morphing_img[j][i] = dst_gray[j][i]
            return Image.fromarray(np.array(np.uint8(morphing_img)))
        else:
            src_r, src_g, src_b = self.src_img.convert('RGB').split()
            dst_r, dst_g, dst_b = self.dst_img.convert('RGB').split()
            dst_r = np.array(dst_r)
            dst_g = np.array(dst_g)
            dst_b = np.array(dst_b)
            src_r = np.array(src_r)
            src_g = np.array(src_g)
            src_b = np.array(src_b)
            dst_y, dst_x = dst_r.shape
            morphing_r = np.zeros((dst_y, dst_x), dtype='float')
            morphing_g = np.zeros((dst_y, dst_x), dtype='float')
            morphing_b = np.zeros((dst_y, dst_x), dtype='float')
            dist_map = self._build_distance_map(dst_r)
            dist_re_map = self._build_distance_reverse_map(dist_map)
            for j in range(dst_y):
                for i in range(dst_x):
                    position_state = self._check_in_bar(bar_list[:4], (i, j))
                    if (i, j) in self.dst_src_points_dict:
                        t_x, t_y = self.dst_src_points_dict[(i, j)]
                        morphing_r[j][i] = src_r[t_y][t_x]
                        morphing_r[j][i] = src_g[t_y][t_x]
                        morphing_r[j][i] = src_b[t_y][t_x]
                    elif position_state == 'in':
                        total_distance = 0
                        t_x = 0
                        t_y = 0
                        for x, y in self.dst_src_points_dict:
                            src_x, src_y = self.dst_src_points_dict[(x, y)]
                            reverse_distance = self._distance_reverse(
                                (i, j), (x, y), dist_re_map)
                            total_distance += reverse_distance
                            t_x += (src_x - x + i) * reverse_distance
                            t_y += (src_y - y + j) * reverse_distance
                        t_x /= total_distance
                        t_y /= total_distance
                        morphing_r[j][i] = self._interpolation((t_x, t_y), src_r)
                        morphing_g[j][i] = self._interpolation((t_x, t_y), src_g)
                        morphing_b[j][i] = self._interpolation((t_x, t_y), src_b)
                    else:
                        morphing_r[j][i] = dst_r[j][i]
                        morphing_g[j][i] = dst_g[j][i]
                        morphing_b[j][i] = dst_b[j][i]
            return Image.merge('RGB', (Image.fromarray(np.uint8(morphing_r)),
                                       Image.fromarray(np.uint8(morphing_g)),
                                       Image.fromarray(np.uint8(morphing_b))))

    @staticmethod
    def _is_triangle_or_area(x1, y1, x2, y2, x3, y3):
        """Calculate the triangle area."""
        return abs((x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2)) / 2.0)

    def _in_triangle(self, t, p):
        """Check whether the point in the triangle.

        Args:
            t: [(x1, y1), (x2, y2), (x3, y3)]
            p: x, y
        """
        [x1, y1], [x2, y2], [x3, y3] = t
        x, y = p
        return (self._is_triangle_or_area(x1, y1, x2, y2, x3, y3) ==
                self._is_triangle_or_area(x, y, x2, y2, x3, y3) +
                self._is_triangle_or_area(x1, y1, x, y, x3, y3) +
                self._is_triangle_or_area(x1, y1, x2, y2, x, y))

    def _build_triangle_map(self, triangle_list):
        """Set the index in triangle_list to a dst map

        Args:
            triangle_list: [[(x1, y1), (x2, y2), (x3, y3)],...]

        Returns:
            triangle_map size: self.dst_img.size
        """
        triangle_map = -np.ones((self.dst_img.size[1], self.dst_img.size[0]), dtype='int')
        for i in range(len(triangle_list)):
            trg = triangle_list[i]
            p1 = trg[0]
            p2 = trg[1]
            p3 = trg[2]
            x_min = min([p1[0], p2[0], p3[0]])
            y_min = min([p1[1], p2[1], p3[1]])
            x_max = max([p1[0], p2[0], p3[0]])
            y_max = max([p1[1], p2[1], p3[1]])
            for j in range(int(x_min), int(x_max)):
                for k in range(int(y_min), int(y_max)):
                    if self._in_triangle(trg, [j, k]):
                        triangle_map[k][j] = i
        return triangle_map

    def advanced_morphing(self):
        """Advanced morphing from source image to destination image.

        You can choose mode 'gray' or 'RGB' by setting mode.

        Returns:
            New image object
        """
        now_dst_src_points_dict = self.dst_src_points_dict.copy()
        if self.dst_img.size[0] > self.result_x \
                or self.dst_img.size[1] > self.result_y:
            rate = min([self.result_x / self.dst_img.size[0],
                        self.result_y / self.dst_img.size[1]])
            self.dst_img = self.dst_img.resize((
                int(rate * self.dst_img.size[0]) - 1,
                int(rate * self.dst_img.size[1]) - 1))
            new_dict = {
                (int(i * rate), int(j * rate)):
                    now_dst_src_points_dict[(i, j)]
                for (i, j) in now_dst_src_points_dict}
            now_dst_src_points_dict = new_dict
        if self.src_img.size[0] < self.dst_img.size[0] \
                or self.src_img.size[0] < self.dst_img.size[1]:
            rate = max([self.dst_img.size[0] / self.src_img.size[1],
                        self.dst_img.size[1] / self.src_img.size[0]])
            self.src_img = self.src_img.resize((
                int(rate * self.src_img.size[0]) + 1,
                int(rate * self.src_img.size[1]) + 1))
            new_dict = {
                (i, j):
                    (int(now_dst_src_points_dict[(i, j)][0] * rate),
                     int(now_dst_src_points_dict[(i, j)][1] * rate))
                for (i, j) in now_dst_src_points_dict}
            now_dst_src_points_dict = new_dict
        if self.flag:
            if (0, 0) not in now_dst_src_points_dict:
                now_dst_src_points_dict[(0, 0)] = (0, 0)
            if (0, self.dst_img.size[1] - 1) not in now_dst_src_points_dict:
                now_dst_src_points_dict[(0, self.dst_img.size[1] - 1)] \
                    = (0, self.src_img.size[1] - 1)
            if (self.dst_img.size[0] - 1, 0) not in now_dst_src_points_dict:
                now_dst_src_points_dict[(self.dst_img.size[0] - 1, 0)] \
                    = (self.src_img.size[0] - 1, 0)
            if (self.dst_img.size[0] - 1,
                    self.dst_img.size[1] - 1) not in now_dst_src_points_dict:
                now_dst_src_points_dict[(self.dst_img.size[0] - 1,
                                         self.dst_img.size[1] - 1)] \
                    = (self.src_img.size[0] - 1, self.src_img.size[1] - 1)
        sub_div = Subdiv2D((0, 0, self.dst_img.size[0], self.dst_img.size[1]))
        for p in now_dst_src_points_dict:
            sub_div.insert(p)
        triangle_list = sub_div.getTriangleList()
        triangle_list_clean = []
        for triangle in triangle_list:
            if ((int(triangle[0]), int(triangle[1])) in now_dst_src_points_dict
                and (int(triangle[2]), int(triangle[3])) in now_dst_src_points_dict
                    and (int(triangle[4]), int(triangle[5])) in now_dst_src_points_dict):
                triangle_list_clean.append([(int(triangle[0]), int(triangle[1])),
                                            (int(triangle[2]), int(triangle[3])),
                                            (int(triangle[4]), int(triangle[5]))])
        triangle_list = triangle_list_clean
        triangle_map = self._build_triangle_map(triangle_list)
        src_r, src_g, src_b = self.src_img.convert('RGB').split()
        dst_r, dst_g, dst_b = self.dst_img.convert('RGB').split()
        dst_r = np.array(dst_r)
        dst_g = np.array(dst_g)
        dst_b = np.array(dst_b)
        src_r = np.array(src_r)
        src_g = np.array(src_g)
        src_b = np.array(src_b)
        dst_y, dst_x = dst_r.shape
        morphing_r = np.zeros((dst_y, dst_x), dtype='float')
        morphing_g = np.zeros((dst_y, dst_x), dtype='float')
        morphing_b = np.zeros((dst_y, dst_x), dtype='float')
        dist_map = self._build_distance_map(dst_r)
        dist_re_map = self._build_distance_reverse_map(dist_map)
        for j in range(dst_y):
            for i in range(dst_x):
                if (i, j) in now_dst_src_points_dict:
                    t_x, t_y = now_dst_src_points_dict[(i, j)]
                    morphing_r[j][i] = src_r[t_y][t_x]
                    morphing_r[j][i] = src_g[t_y][t_x]
                    morphing_r[j][i] = src_b[t_y][t_x]
                else:
                    triangle_index = triangle_map[j][i]
                    if triangle_index > -1:
                        triangle = triangle_list[triangle_index]
                        total_distance = 0
                        t_x = 0
                        t_y = 0
                        for x, y in triangle:
                            current_src_x, current_src_y = now_dst_src_points_dict[(x, y)]
                            reverse_distance = self._distance_reverse(
                                (i, j), (x, y), dist_re_map)
                            total_distance += reverse_distance
                            t_x += (current_src_x - x + i) * reverse_distance
                            t_y += (current_src_y - y + j) * reverse_distance
                        t_x /= total_distance
                        t_y /= total_distance
                        morphing_r[j][i] = self._interpolation((t_x, t_y), src_r)
                        morphing_g[j][i] = self._interpolation((t_x, t_y), src_g)
                        morphing_b[j][i] = self._interpolation((t_x, t_y), src_b)
                    else:
                        morphing_r[j][i] = dst_r[j][i]
                        morphing_g[j][i] = dst_g[j][i]
                        morphing_b[j][i] = dst_b[j][i]
        new_img = Image.merge('RGB', (Image.fromarray(np.uint8(morphing_r)),
                                      Image.fromarray(np.uint8(morphing_g)),
                                      Image.fromarray(np.uint8(morphing_b))))
        if self.mode == 'gray':
            new_img = Image.fromarray(np.array(np.uint8(
                np.array(new_img.convert('L')))))
            new_img.save(os.path.join(os.getcwd(), 'result.jpg'))
            new_img.show()
            return new_img
        else:
            new_img.save(os.path.join(os.getcwd(), 'result.jpg'))
            new_img.show()
            return new_img

    def default_run(self):
        """Default run of the class.

        Make sure the two image file zxh-ape.jpg and ape.jpg exist.

        Returns:
            A new image morphing two sample images
        """
        src_points = [(327, 387), (420, 387), (521, 372), (609, 364),  # Eyes
                      (426, 477), (471, 491), (524, 472),  # Nose
                      (410, 566), (442, 569), (475, 569), (507, 567), (550, 551)]  # Mouth
        dst_points = [(68, 27), (110, 38), (145, 34), (184, 24),  # Eyes
                      (81, 179), (116, 190), (163, 184),  # Nose
                      (46, 173), (72, 218), (116, 237), (164, 233), (199, 205)]  # Mouth
        self.set_src_path('zxh-ape.jpg')
        self.set_dst_path('ape.jpg')
        self.open_src_img()
        self.open_dst_img()
        self.set_points(src_points, dst_points)
        return self.morphing()
