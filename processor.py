import cv2
import numpy as np
import streamlit as st

from detector import detect, model
from roi import is_in_roi


def process_frame(frame, roi_points, cam_name):

    current_helmet = 0
    current_nohelmet = 0
    current_danger = 0

    frame = cv2.resize(frame, (800,800))

    roi_poly = np.array(
        roi_points,
        dtype=np.int32
    )

    results = detect(frame)


    for r in results:

        if r.boxes is None:
            continue

        if r.boxes.id is None:
            continue


        ids = r.boxes.id.int().cpu().tolist()

        boxes = r.boxes.xyxy.int().cpu().tolist()

        classes = r.boxes.cls.int().cpu().tolist()


        for tid, box, cls in zip(ids, boxes, classes):

            x1,y1,x2,y2 = box

            name = model.names[cls].lower()

            unique_id = f"{cam_name}_{tid}"


            in_zone = is_in_roi(

                roi_poly,

                x1,

                y1,

                x2,

                y2

            )


            # -----------------------
            # Helmet
            # -----------------------

            if name == "helmet":

                current_helmet += 1


                if unique_id not in st.session_state.helmet_ids:

                    st.session_state.helmet_ids.add(unique_id)


                cv2.rectangle(

                    frame,

                    (x1,y1),

                    (x2,y2),

                    (0,255,0),      # 초록

                    3

                )


            # -----------------------
            # No Helmet
            # -----------------------

            elif name in ["no-helmet", "nohelmet"]:


                current_nohelmet += 1


                if unique_id not in st.session_state.nohelmet_ids:

                    st.session_state.nohelmet_ids.add(unique_id)


                cv2.rectangle(

                    frame,

                    (x1,y1),

                    (x2,y2),

                    (0,255,255),    # 노랑

                    3

                )


                cv2.putText(

                    frame,

                    "NO HELMET",

                    (x1,y1-10),

                    cv2.FONT_HERSHEY_SIMPLEX,

                    0.7,

                    (0,255,255),

                    2

                )


            # -----------------------
            # Person + ROI = Danger
            # -----------------------

            elif name == "person":


                if in_zone:


                    current_danger += 1


                    if unique_id not in st.session_state.danger_ids:

                        st.session_state.danger_ids.add(unique_id)


                    cv2.rectangle(

                        frame,

                        (x1,y1),

                        (x2,y2),

                        (0,0,255),     # 빨강

                        3

                    )


                    cv2.putText(

                        frame,

                        "DANGER",

                        (x1,y1-10),

                        cv2.FONT_HERSHEY_SIMPLEX,

                        0.7,

                        (0,0,255),

                        2

                    )


    # -----------------------
    # ROI 표시
    # -----------------------

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

        3

    )


    return (

        frame,

        current_helmet,

        current_danger,

        current_nohelmet

    )