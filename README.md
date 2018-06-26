# Face-Morphing

### Method
1. Run `main.py` to run the app.
2. Run `sample_face_morphing.py` to run the test file. **Make sure the Face++ API can work when testing.**

### Code Structure
#### `face_morphing.py` 

- Set images and points to be morphed.
- Get the morphed image.
- Select morphing mode.
- Back-end of the application.

##### Class

- **FaceMorphing**
  
##### Simple example:
```
fm = FaceMorphing()
fm.set_src_path('zxh-ape.jpg')
fm.set_dst_path('ape.jpg')
src_img = fm.open_src_img()
dst_img = fm.open_dst_img()
fm.set_points(zxh_points, ape_points)
new_img = fm.morphing() (or fm.advanced_morphing())
# And then you can show the three image:
#   src_img, dst_img, new_img
```

##### Parameter settings:

- Set fm.mode to choose either gray or rgb mode
- Set fm.distance_mode to choose either Euler or Manhattan distance
- Set fm.flag to determine only-face morphing or whole image morphing

**Remember**: set the mode before morphing or it will use default.

If face++ cannot work well, you can also change the id and password of Face++ API in auto_select_points settings

#### `ui.py`

- Front-end 

##### Class

- ViewLabel: Label class that can be draw painter on.
- PaintLabel: Label class that can be draw painter on when clicked.
- PointChooseUI: Sub-window to choose the points.
- FaceMorphingUI: Main Window.

#### `sample_face_morphing.py`
Run the test.

#### `main.py`
Run the application.