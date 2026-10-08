from zones.geometry import bottom_center,point_in_polygon,crosses_line
def test_bottom_center(): assert bottom_center((0,1,10,20)) == (5,20)
def test_polygon(): assert point_in_polygon((5,5),[(0,0),(10,0),(10,10),(0,10)])
def test_crossing(): assert crosses_line((0,0),(10,0),[(5,-5),(5,5)])
