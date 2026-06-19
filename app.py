import streamlit as st
import cv2
import tempfile
from datetime import datetime
import pandas as pd
import plotly.express as px

import processor
from roi_selector import set_roi_interactive


# =====================================
# PAGE CONFIG
# =====================================

st.set_page_config(

    page_title="SafeCap AI",

    page_icon="🦺",

    layout="wide"

)



# =====================================
# SESSION STATE
# =====================================

if "helmet_ids" not in st.session_state:

    st.session_state.helmet_ids = set()



if "nohelmet_ids" not in st.session_state:

    st.session_state.nohelmet_ids = set()



if "danger_ids" not in st.session_state:

    st.session_state.danger_ids = set()



if "logs" not in st.session_state:

    st.session_state.logs = []


if "logged_danger_ids" not in st.session_state:

    st.session_state.logged_danger_ids = set()


# =====================================
# SAVE VIDEO
# =====================================

def save_uploaded_file(uploaded_file):

    with tempfile.NamedTemporaryFile(

        delete=False,

        suffix=".mp4"

    ) as tmp:


        tmp.write(

            uploaded_file.read()

        )


        return tmp.name




# =====================================
# TITLE
# =====================================

st.title("🦺 SafeCap AI")

st.caption(

    "실시간 안전모 착용 및 위험구역 침입 감지 시스템"

)



# =====================================
# SIDEBAR
# =====================================

st.sidebar.header("⚙️ ROI 설정")



show_roi = st.sidebar.checkbox(

    "위험구역 표시",

    value=True

)



roi_alpha = st.sidebar.slider(

    "위험구역 투명도",

    min_value=0.0,

    max_value=1.0,

    value=0.4,

    step=0.05

)




# =====================================
# KPI PLACEHOLDER
# =====================================

k1,k2,k3,k4 = st.columns(4)


helmet_metric = k1.empty()

nohelmet_metric = k2.empty()

danger_metric = k3.empty()

cctv_metric = k4.empty()



helmet_metric.metric(

    "⛑ Helmet",

    0

)



nohelmet_metric.metric(

    "❌ No Helmet",

    0

)



danger_metric.metric(

    "🚨 Danger",

    0

)



cctv_metric.metric(

    "📹 CCTV",

    2

)



st.write("---")


# =====================================
# VIDEO UPLOAD
# =====================================

u1, u2 = st.columns(2)


with u1:

    video1 = st.file_uploader(

        "📹 CCTV1",

        type=["mp4","avi"],

        key="video1"

    )



with u2:

    video2 = st.file_uploader(

        "📹 CCTV2",

        type=["mp4","avi"],

        key="video2"

    )



# =====================================
# START BUTTON
# =====================================

start = st.button(

    "▶ 분석 시작",

    use_container_width=True,

    key="start_button"

)



st.write("---")



# =====================================
# DASHBOARD LAYOUT
# =====================================

left, right = st.columns(

    [3,1]

)



# =====================================
# LEFT : LIVE MONITORING
# =====================================

with left:


    st.subheader("📡 실시간 모니터링")


    cam1, cam2 = st.columns(2)



    # 영상 출력용

    frame_area1 = cam1.empty()

    frame_area2 = cam2.empty()



    # CCTV 상태 출력용

    info_area1 = cam1.empty()

    info_area2 = cam2.empty()




# =====================================
# RIGHT : LIVE LOG
# =====================================

with right:


    st.subheader("🚨 실시간 로그")


    log_area = st.empty()




st.write("---")


# =====================================
# START ANALYSIS
# =====================================

if start:

    if video1 is None or video2 is None:

        st.warning(

            "두 개의 영상을 업로드해주세요."

        )

        st.stop()



    # -----------------------------
    # SAVE VIDEO
    # -----------------------------

    path1 = save_uploaded_file(video1)

    path2 = save_uploaded_file(video2)



    # -----------------------------
    # ROI SELECT
    # -----------------------------

    st.info(

        "CCTV1 위험구역 선택 후 Enter"

    )


    roi1 = set_roi_interactive(

        path1,

        "ROI CCTV1"

    )



    st.info(

        "CCTV2 위험구역 선택 후 Enter"

    )


    roi2 = set_roi_interactive(

        path2,

        "ROI CCTV2"

    )



    # -----------------------------
    # OPEN VIDEO
    # -----------------------------

    cap1 = cv2.VideoCapture(path1)

    cap2 = cv2.VideoCapture(path2)



    # -----------------------------
    # VIDEO LOOP
    # -----------------------------

    while True:


        ret1, frame1 = cap1.read()

        ret2, frame2 = cap2.read()



        if not ret1 and not ret2:

            break



        # =========================
        # CCTV1
        # =========================

        if ret1:


            frame1, h1, d1, n1 = processor.process_frame(

                frame1,

                roi1,

                "cam1",

                show_roi,

                roi_alpha

            )



            frame_area1.image(

                frame1,

                channels="BGR",

                use_container_width=True

            )



            with info_area1.container():

                st.markdown("### 📹 CCTV1")

                st.success("🟢 LIVE")

                st.write(f"⛑ Helmet : {h1}")

                st.write(f"❌ No Helmet : {n1}")

                st.write(f"🚨 Danger : {d1}")



            if d1 > 0:

                now = datetime.now().strftime("%H:%M:%S")


                st.session_state.logs.append(

                    f"🚨 {now} CCTV1 Danger"

                )



        # =========================
        # CCTV2
        # =========================

        if ret2:


            frame2, h2, d2, n2 = processor.process_frame(

                frame2,

                roi2,

                "cam2",

                show_roi,

                roi_alpha

            )



            frame_area2.image(

                frame2,

                channels="BGR",

                use_container_width=True

            )



            with info_area2.container():

                st.markdown("### 📹 CCTV2")

                st.success("🟢 LIVE")

                st.write(f"⛑ Helmet : {h2}")

                st.write(f"❌ No Helmet : {n2}")

                st.write(f"🚨 Danger : {d2}")



            if d2 > 0:

                now = datetime.now().strftime("%H:%M:%S")


                st.session_state.logs.append(

                    f"🚨 {now} CCTV2 Danger"

                )



        # =========================
        # KPI UPDATE
        # =========================

        helmet_metric.metric(

            "⛑ Helmet",

            len(st.session_state.helmet_ids)

        )


        nohelmet_metric.metric(

            "❌ No Helmet",

            len(st.session_state.nohelmet_ids)

        )


        danger_metric.metric(

            "🚨 Danger",

            len(st.session_state.danger_ids)

        )



        # =========================
        # LIVE LOG
        # =========================

        with log_area.container():

            for log in reversed(

                st.session_state.logs[-5:]

            ):

                st.warning(log)



    # -----------------------------
    # RELEASE
    # -----------------------------

    cap1.release()

    cap2.release()



    st.success(

        "✅ 영상 분석 완료"

    )

# =====================================
# FINAL DASHBOARD
# =====================================

st.write("---")

st.subheader("📊 최종 탐지 통계")


chart_col, stat_col = st.columns([2,1])



# =====================================
# DONUT CHART
# =====================================

with chart_col:

    df = pd.DataFrame({

        "Class":[

            "Helmet",

            "No Helmet",

        ],

        "Count":[

            len(st.session_state.helmet_ids),

            len(st.session_state.nohelmet_ids),

        ]

    })



    fig = px.pie(

        df,

        names="Class",

        values="Count",

        hole=0.55,
        
        color="Class",

        color_discrete_map={

        "Helmet":"#10B981",      

        "No Helmet":"#F59E0B",   
        }
    )

    fig.update_traces(

        textinfo="percent",

        marker=dict(

            line=dict(

                color="#0E1117",

                width=5

            )

        )
    )



    fig.update_layout(

        paper_bgcolor="#0E1117",

        plot_bgcolor="#0E1117",

        font_color="white",

        legend_font_color="white"

    )



    st.plotly_chart(

        fig,

        use_container_width=True

    )



# =====================================
# SUMMARY CARD
# =====================================

with stat_col:


    st.metric(

        "⛑ Helmet",

        len(st.session_state.helmet_ids)

    )


    st.metric(

        "❌ No Helmet",

        len(st.session_state.nohelmet_ids)

    )


    st.metric(

        "🚨 Danger",

        len(st.session_state.logged_danger_ids)

    )



st.write("---")



# =====================================
# RECENT EVENTS
# =====================================

st.subheader("📌 최근 이벤트")



if len(st.session_state.logs)==0:

    st.info(

        "이벤트가 없습니다."

    )



else:


    for log in reversed(

        st.session_state.logs[-10:]

    ):


        st.warning(log)