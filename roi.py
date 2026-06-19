import cv2


def is_in_roi(roi_poly, x1, y1, x2, y2):

    points = [

        (x1, y1),

        (x2, y1),

        (x1, y2),

        (x2, y2),

        ((x1+x2)//2, (y1+y2)//2)

    ]


    for p in points:

        if cv2.pointPolygonTest(

            roi_poly,

            p,

            False

        ) >= 0:

            return True


    return False