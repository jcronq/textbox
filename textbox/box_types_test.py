from textbox import box_types


def test_dimensions():
    test = box_types.Dimensions(3, 4)
    assert test.height == 3
    assert test.width == 4
    assert test.area == test.height * test.width


def test_position():
    test1 = box_types.Position(3, 4)
    test2 = box_types.Position(1, 2)
    assert test1.lineno == 3
    assert test1.colno == 4
    assert test1 + test2 == box_types.Position(4, 6)
    assert test1 - test2 == box_types.Position(2, 2)
    assert test2 - test1 == box_types.Position(-2, -2)


def test_boundingbox():
    test = box_types.BoundingBox(1, 2, 3, 4)
    assert test.lineno == 1
    assert test.colno == 2
    assert test.height == 3
    assert test.width == 4
    assert test.first_lineno == 1
    assert test.last_lineno == 3
    assert test.first_colno == 2
    assert test.last_colno == 5
    assert test.top_left == box_types.Position(1, 2)
    assert test.bottom_left == box_types.Position(3, 2)
    assert test.top_right == box_types.Position(1, 5)
    assert test.bottom_right == box_types.Position(3, 5)


def test_boundingbox_contains_position():
    test_box = box_types.BoundingBox(0, 0, 2, 4)
    assert box_types.Position(0, 0) in test_box
    assert box_types.Position(-1, 0) not in test_box
    assert box_types.Position(-1, -1) not in test_box
    assert box_types.Position(0, -1) not in test_box

    assert box_types.Position(1, 3) in test_box
    assert box_types.Position(2, 3) not in test_box
    assert box_types.Position(2, 4) not in test_box
    assert box_types.Position(1, 4) not in test_box

    assert box_types.Position(0, 3) in test_box
    assert box_types.Position(0, 4) not in test_box
    assert box_types.Position(-1, 4) not in test_box
    assert box_types.Position(-1, 3) not in test_box

    assert box_types.Position(1, 0) in test_box
    assert box_types.Position(2, 0) not in test_box
    assert box_types.Position(1, -1) not in test_box
    assert box_types.Position(2, -1) not in test_box


def test_boundingbox_contains_box():
    test_box = box_types.BoundingBox(0, 0, 2, 4)
    assert box_types.BoundingBox(0, 0, 2, 4) in test_box
    assert box_types.BoundingBox(0, 0, 1, 4) in test_box
    assert box_types.BoundingBox(0, 0, 2, 3) in test_box
    assert box_types.BoundingBox(0, 0, 1, 3) in test_box
    assert box_types.BoundingBox(0, 0, 1, 1) in test_box
    assert box_types.BoundingBox(0, 0, 2, 1) in test_box
    assert box_types.BoundingBox(0, 0, 1, 2) in test_box
    assert box_types.BoundingBox(0, 0, 2, 2) in test_box
    assert box_types.BoundingBox(0, 0, 0, 2) in test_box
    assert box_types.BoundingBox(0, 0, 0, 1) in test_box
    assert box_types.BoundingBox(0, 0, 2, 0) in test_box
    assert box_types.BoundingBox(0, 0, 1, 0) in test_box
    assert box_types.BoundingBox(0, 0, 0, 0) in test_box

    assert box_types.BoundingBox(0, 1, 2, 3) in test_box
    assert box_types.BoundingBox(0, 1, 1, 3) in test_box
    assert box_types.BoundingBox(0, 1, 1, 1) in test_box
    assert box_types.BoundingBox(0, 1, 1, 2) in test_box
    assert box_types.BoundingBox(0, 1, 2, 1) in test_box
    assert box_types.BoundingBox(0, 1, 2, 2) in test_box

    assert box_types.BoundingBox(0, 1, 2, 3) in test_box
    assert box_types.BoundingBox(0, 1, 1, 3) in test_box
    assert box_types.BoundingBox(0, 1, 1, 1) in test_box
    assert box_types.BoundingBox(0, 1, 1, 2) in test_box
    assert box_types.BoundingBox(0, 1, 2, 1) in test_box
    assert box_types.BoundingBox(0, 1, 2, 2) in test_box

    assert box_types.BoundingBox(0, 0, 3, 4) not in test_box
    assert box_types.BoundingBox(0, 0, 2, 5) not in test_box
    assert box_types.BoundingBox(0, 0, 3, 5) not in test_box

    assert box_types.BoundingBox(1, 0, 2, 4) not in test_box
    assert box_types.BoundingBox(-1, 0, 2, 4) not in test_box
    assert box_types.BoundingBox(0, 1, 2, 4) not in test_box
    assert box_types.BoundingBox(0, -1, 2, 4) not in test_box
