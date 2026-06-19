import cv2
import numpy as np

def set_roi_interactive(video_path, window_name):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(fps))

    ret, frame = cap.read()
    if not ret:
        cap.release()
        return [[50,50], [750,50], [750,750], [50,750]]

    # ROI 선택 화면 크기 (processor.py의 크기와 동일해야 함)
    frame = cv2.resize(frame, (800,800))
    points = []

    def mouse_callback(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            points.append([x, y])

    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 900, 900)
    cv2.setMouseCallback(window_name, mouse_callback)

    while True:
        display = frame.copy()
        
        # 클릭한 점 표시
        for p in points:
            cv2.circle(display, tuple(p), 6, (0,0,255), -1)
            
        # 선 연결
        if len(points) > 1:
            cv2.polylines(display, [np.array(points, np.int32)], False, (0,255,255), 2)
            
        cv2.putText(display, f"Points : {len(points)}", (20,40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
        cv2.putText(display, "Left Click : Add Point", (20,80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)
        cv2.putText(display, "Press Enter : Finish", (20,120), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)

        cv2.imshow(window_name, display)
        key = cv2.waitKey(20)

        # 엔터키(13)를 누르면 종료
        if key == 13 and len(points) >= 3:
            break

    cap.release()
    cv2.destroyWindow(window_name)
    cv2.waitKey(1) # Mac/Windows 잔여 창 버그 방지용

    return points