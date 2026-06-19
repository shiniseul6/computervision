import streamlit as st
import cv2
import tempfile

import processor
from roi_selector import set_roi_interactive


st.set_page_config(
    page_title="SafeCap AI",
    layout="wide"
)


# --------------------
# Session State
# --------------------

if "helmet_ids" not in st.session_state:
    st.session_state.helmet_ids = set()

if "nohelmet_ids" not in st.session_state:
    st.session_state.nohelmet_ids = set()

if "danger_ids" not in st.session_state:
    st.session_state.danger_ids = set()

if "show_result" not in st.session_state:
    st.session_state.show_result = False


# --------------------
# Save Video
# --------------------

def save_uploaded_file(uploaded_file):

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".mp4"
    ) as tmp:

        tmp.write(uploaded_file.read())

        return tmp.name


# --------------------
# UI
# --------------------

st.title("🦺 SafeCap AI 실시간 관제")

c1, c2 = st.columns([1,1], gap="large")

with c1:

    video1 = st.file_uploader(

        "CCTV1",

        type=["mp4","avi"]

    )


with c2:

    video2 = st.file_uploader(

        "CCTV2",

        type=["mp4","avi"]

    )



# --------------------
# START
# --------------------

if st.button("▶ 분석 시작"):


    if video1 is None or video2 is None:

        st.warning(

            "두 개의 영상을 모두 업로드해주세요."

        )

        st.stop()


    path1 = save_uploaded_file(video1)

    path2 = save_uploaded_file(video2)



    # ROI 선택

    st.info(

        "CCTV1 위험구역을 클릭 후 Enter"

    )

    roi1 = set_roi_interactive(

        path1,

        "ROI CCTV1"

    )


    st.info(

        "CCTV2 위험구역을 클릭 후 Enter"

    )

    roi2 = set_roi_interactive(

        path2,

        "ROI CCTV2"

    )



    cap1 = cv2.VideoCapture(path1)

    cap2 = cv2.VideoCapture(path2)



    col1, col2 = st.columns(

        [1,1],

        gap="large"

    )


    frame_area1 = col1.empty()

    frame_area2 = col2.empty()


    info1 = col1.empty()

    info2 = col2.empty()



    while cap1.isOpened() or cap2.isOpened():


        ret1, frame1 = cap1.read()

        ret2, frame2 = cap2.read()


        if not ret1 and not ret2:

            break



        # -------------------
        # CCTV1
        # -------------------

        if ret1:


            frame1, h1, d1, n1 = processor.process_frame(

                frame1,

                roi1,

                "cam1"

            )


            frame_area1.image(

                frame1,

                channels="BGR"

            )


            info1.markdown(

                f"""

### CCTV1

⛑ Helmet : {h1}

❌ No Helmet : {n1}

🚨 Danger : {d1}

"""

            )



        # -------------------
        # CCTV2
        # -------------------

        if ret2:


            frame2, h2, d2, n2 = processor.process_frame(

                frame2,

                roi2,

                "cam2"

            )


            frame_area2.image(

                frame2,

                channels="BGR"

            )


            info2.markdown(

                f"""

### CCTV2

⛑ Helmet : {h2}

❌ No Helmet : {n2}

🚨 Danger : {d2}

"""

            )



    cap1.release()

    cap2.release()


    st.success(

        "영상 분석 완료"

    )


    st.session_state.show_result = True




# --------------------
# Final Result
# --------------------

if st.session_state.show_result:


    st.write("---")


    st.subheader(

        "📊 최종 누적 결과"

    )


    c1, c2, c3 = st.columns(3)


    c1.metric(

        "⛑ Helmet",

        len(st.session_state.helmet_ids)

    )


    c2.metric(

        "❌ No Helmet",

        len(st.session_state.nohelmet_ids)

    )


    c3.metric(

        "🚨 Danger",

        len(st.session_state.danger_ids)

    )