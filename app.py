import streamlit as st
import cv2
import tempfile
import numpy as np
from ultralytics import YOLO

# --------------------------------
# 1. 페이지 설정
# --------------------------------

st.set_page_config(
    layout="wide",
    page_title="SafeCap AI Monitoring"
)

st.title("🏭 CCTV Safety Monitoring System")


# --------------------------------
# 2. 모델 로드
# --------------------------------

@st.cache_resource
def load_model():

    model = YOLO("best.pt")

    return model


model = load_model()


# --------------------------------
# 3. 업로드 파일 저장
# --------------------------------

def save_uploaded_file(uploaded_file):

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".mp4"
    ) as tmp:

        tmp.write(uploaded_file.read())

        return tmp.name


# --------------------------------
# 4. ROI 설정
# --------------------------------

def set_roi_interactive(video_path, window_name):

    cap = cv2.VideoCapture(video_path)

    fps = cap.get(cv2.CAP_PROP_FPS)

    cap.set(
        cv2.CAP_PROP_POS_FRAMES,
        int(fps)
    )

    ret, frame = cap.read()

    if not ret:

        cap.release()

        return [

            [50,50],

            [450,50],

            [450,450],

            [50,450]

        ]


    frame = cv2.resize(frame,(500,500))

    points=[]


    def mouse_callback(event,x,y,flags,param):

        if event==cv2.EVENT_LBUTTONDOWN:

            points.append([x,y])



    cv2.namedWindow(window_name)

    cv2.setMouseCallback(

        window_name,

        mouse_callback

    )


    while True:

        display=frame.copy()


        if len(points)>0:

            for p in points:

                cv2.circle(

                    display,

                    tuple(p),

                    5,

                    (0,0,255),

                    -1

                )


            if len(points)>1:

                cv2.polylines(

                    display,

                    [np.array(points,np.int32)],

                    False,

                    (0,255,255),

                    2

                )



        cv2.putText(

            display,

            f"Points : {len(points)}",

            (20,30),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.7,

            (0,255,0),

            2

        )


        cv2.imshow(

            window_name,

            display

        )


        if (

            cv2.waitKey(1)==13

            and

            len(points)>=3

        ):

            break


    cap.release()

    cv2.destroyWindow(window_name)

    return points


# --------------------------------
# 5. Session State
# --------------------------------

if 'roi_cam1' not in st.session_state:

    st.session_state.roi_cam1=None


if 'roi_cam2' not in st.session_state:

    st.session_state.roi_cam2=None


if 'path_cam1' not in st.session_state:

    st.session_state.path_cam1=None


if 'path_cam2' not in st.session_state:

    st.session_state.path_cam2=None


# ID 누적


if 'helmet_ids' not in st.session_state:

    st.session_state.helmet_ids=set()


if 'nohelmet_ids' not in st.session_state:

    st.session_state.nohelmet_ids=set()


if 'danger_ids' not in st.session_state:

    st.session_state.danger_ids=set()


# --------------------------------
# 6. Sidebar
# --------------------------------

with st.sidebar:

    st.header("📐 위험 구역 설정")


    v1=st.file_uploader(

        "📹 CCTV1",

        type=["mp4","avi"]

    )


    if v1:

        st.session_state.path_cam1=save_uploaded_file(v1)


        if st.button("🟥 CCTV1 ROI"):

            st.session_state.roi_cam1=\
            set_roi_interactive(

                st.session_state.path_cam1,

                "CCTV1"

            )


    st.divider()



    v2=st.file_uploader(

        "📹 CCTV2",

        type=["mp4","avi"]

    )


    if v2:

        st.session_state.path_cam2=save_uploaded_file(v2)


        if st.button("🟥 CCTV2 ROI"):

            st.session_state.roi_cam2=\
            set_roi_interactive(

                st.session_state.path_cam2,

                "CCTV2"

            )

# --------------------------------
# 7. 분석 로직 (YOLO Track)
# --------------------------------

def process_frame(frame, roi_points):

    current_helmet = 0
    current_nohelmet = 0
    current_danger = 0

    frame = cv2.resize(frame, (500, 500))

    roi_poly = np.array(
        roi_points,
        dtype=np.int32
    )

    results = model.track(

        frame,

        persist=True,

        tracker="bytetrack.yaml",

        conf=0.15,

        iou=0.5,

        verbose=False

    )


    for r in results:

        if r.boxes.id is None:

            continue


        ids = r.boxes.id.int().cpu().tolist()

        boxes = r.boxes.xyxy.int().cpu().tolist()

        classes = r.boxes.cls.int().cpu().tolist()


        for tid, box, cls in zip(

            ids,

            boxes,

            classes

        ):

            x1, y1, x2, y2 = box

            name = model.names[cls].lower()


            # ROI 체크

            points = [

                (x1, y1),

                (x2, y1),

                (x1, y2),

                (x2, y2),

                ((x1+x2)//2, (y1+y2)//2)

            ]


            in_zone = False


            for p in points:

                if cv2.pointPolygonTest(

                    roi_poly,

                    p,

                    False

                ) >= 0:

                    in_zone = True

                    break


            # ==========================
            # HELMET
            # ==========================

            if name == "helmet":

                current_helmet += 1


                if tid not in st.session_state.helmet_ids:

                    st.session_state.helmet_ids.add(tid)


                color = (0,255,255)   # 노란색


                if in_zone:

                    current_danger += 1


                    if tid not in st.session_state.danger_ids:

                        st.session_state.danger_ids.add(tid)


                    color = (0,0,255)


                    cv2.putText(

                        frame,

                        "DANGER",

                        (x1,y1-10),

                        cv2.FONT_HERSHEY_SIMPLEX,

                        0.7,

                        (0,0,255),

                        2

                    )


                cv2.rectangle(

                    frame,

                    (x1,y1),

                    (x2,y2),

                    color,

                    3

                )


            # ==========================
            # HEAD = NO HELMET
            # ==========================

            elif name == "head":

                current_nohelmet += 1


                if tid not in st.session_state.nohelmet_ids:

                    st.session_state.nohelmet_ids.add(tid)


                color = (0,255,255)

                text = "NO HELMET"


                if in_zone:

                    current_danger += 1


                    if tid not in st.session_state.danger_ids:

                        st.session_state.danger_ids.add(tid)


                    color = (0,0,255)

                    text = "DANGER"


                cv2.rectangle(

                    frame,

                    (x1,y1),

                    (x2,y2),

                    color,

                    3

                )


                cv2.putText(

                    frame,

                    text,

                    (x1,y1-10),

                    cv2.FONT_HERSHEY_SIMPLEX,

                    0.7,

                    color,

                    2

                )


    # ==========================
    # ROI 표시
    # ==========================

    overlay = frame.copy()


    cv2.fillPoly(

        overlay,

        [roi_poly],

        (0,0,255)

    )


    frame = cv2.addWeighted(

        overlay,

        0.2,

        frame,

        0.8,

        0

    )


    cv2.polylines(

        frame,

        [roi_poly],

        True,

        (0,0,255),

        2

    )


    return (

        frame,

        current_helmet,

        current_danger,

        current_nohelmet

    )
# --------------------------------
# 8. 메인 실행부
# --------------------------------

st.write("---")

col1, col2 = st.columns(2)

frame_area1 = col1.empty()
frame_area2 = col2.empty()

status1 = col1.empty()
status2 = col2.empty()


if st.button("▶ START BOTH CCTV"):

    # 이전 결과 초기화

    st.session_state.helmet_ids.clear()

    st.session_state.nohelmet_ids.clear()

    st.session_state.danger_ids.clear()


    if (

        st.session_state.path_cam1 is None

        or

        st.session_state.path_cam2 is None

    ):

        st.error(

            "CCTV 1과 CCTV 2 영상을 모두 업로드해주세요."

        )


    else:


        default_roi = [

            [50,50],

            [450,50],

            [450,450],

            [50,450]

        ]


        r1 = (

            st.session_state.roi_cam1

            if st.session_state.roi_cam1

            else default_roi

        )


        r2 = (

            st.session_state.roi_cam2

            if st.session_state.roi_cam2

            else default_roi

        )


        cap1 = cv2.VideoCapture(

            st.session_state.path_cam1

        )


        cap2 = cv2.VideoCapture(

            st.session_state.path_cam2

        )


        while cap1.isOpened() or cap2.isOpened():


            ret1, frame1 = cap1.read()

            ret2, frame2 = cap2.read()


            if not ret1 and not ret2:

                break



            # CCTV1

            if ret1:


                frame1, h1, d1, n1 = process_frame(

                    frame1,

                    r1

                )


                frame_area1.image(

                    frame1,

                    channels="BGR",

                    use_container_width=True

                )


                status1.markdown(

                    f"""

                    ### 📊 CCTV 1

                    ⛑ HELMET : **{h1}**

                    ❌ NO HELMET : **{n1}**

                    🚨 DANGER : **{d1}**

                    """

                )



            # CCTV2

            if ret2:


                frame2, h2, d2, n2 = process_frame(

                    frame2,

                    r2

                )


                frame_area2.image(

                    frame2,

                    channels="BGR",

                    use_container_width=True

                )


                status2.markdown(

                    f"""

                    ### 📊 CCTV 2

                    ⛑ HELMET : **{h2}**

                    ❌ NO HELMET : **{n2}**

                    🚨 DANGER : **{d2}**

                    """

                )



        cap1.release()

        cap2.release()



        st.success("✅ 영상 분석 완료")



        st.markdown("## 📈 최종 누적 결과")


        c1,c2,c3=st.columns(3)


        c1.metric(

            "⛑ HELMET",

            len(st.session_state.helmet_ids)

        )


        c2.metric(

            "❌ NO HELMET",

            len(st.session_state.nohelmet_ids)

        )


        c3.metric(

            "🚨 DANGER",

            len(st.session_state.danger_ids)

        )