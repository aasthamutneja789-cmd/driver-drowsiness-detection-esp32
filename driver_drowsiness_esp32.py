import cv2
import mediapipe as mp
import math
import serial
import time


# ============================================================
# 1. ESP32 SERIAL CONNECTION
# ============================================================

esp32 = serial.Serial(
    "COM7",
    115200,
    timeout=1
)

time.sleep(2)

last_command = None


# ============================================================
# 2. MEDIAPIPE FACE MESH
# ============================================================

mp_face_mesh = mp.solutions.face_mesh

face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)


# ============================================================
# 3. WEBCAM
# ============================================================

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    esp32.close()
    exit()

print("Webcam opened successfully!")
print("ESP32 connected on COM7.")
print("Press 'q' to quit.")


# ============================================================
# 4. EYE LANDMARKS
# ============================================================

LEFT_EYE = [
    (362, 385),
    (385, 387),
    (387, 263),
    (263, 373),
    (373, 380),
    (380, 362)
]

RIGHT_EYE = [
    (33, 160),
    (160, 158),
    (158, 133),
    (133, 153),
    (153, 144),
    (144, 33)
]


# ============================================================
# 5. CALIBRATION VARIABLES
# ============================================================

calibration_frames = 100

open_eye_values = []

baseline = None
EAR_THRESHOLD = None

calibration_complete = False


# ============================================================
# 6. EYE CLOSURE VARIABLES
# ============================================================

closed_frame_count = 0

CLOSED_FRAME_LIMIT = 15

prolonged_closure_detected = False


# ============================================================
# 7. MAIN LOOP
# ============================================================

while True:

    ret, frame = cap.read()

    if not ret:
        print("Error: Could not read frame.")
        break

    rgb_frame = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    results = face_mesh.process(rgb_frame)


    # ========================================================
    # 8. FACE DETECTED
    # ========================================================

    if results.multi_face_landmarks:

        face_landmarks = results.multi_face_landmarks[0]

        height, width, _ = frame.shape


        # ====================================================
        # 9. RIGHT EYE POINTS
        # ====================================================

        P1 = face_landmarks.landmark[33]
        P2 = face_landmarks.landmark[160]
        P3 = face_landmarks.landmark[158]
        P4 = face_landmarks.landmark[133]
        P5 = face_landmarks.landmark[153]
        P6 = face_landmarks.landmark[144]


        # ====================================================
        # 10. EAR DISTANCES
        # ====================================================

        vertical_1 = math.sqrt(
            (P6.x - P2.x) ** 2 +
            (P6.y - P2.y) ** 2
        )

        vertical_2 = math.sqrt(
            (P5.x - P3.x) ** 2 +
            (P5.y - P3.y) ** 2
        )

        horizontal = math.sqrt(
            (P4.x - P1.x) ** 2 +
            (P4.y - P1.y) ** 2
        )


        # ====================================================
        # 11. EAR
        # ====================================================

        EAR = (
            vertical_1 + vertical_2
        ) / (
            2 * horizontal
        )


    

                # ====================================================
        # 12. CALIBRATION
        # ====================================================

        if not calibration_complete:

            # Keep LED and buzzer OFF during calibration
            if last_command != "NORMAL":

                esp32.write(b"NORMAL\n")

                last_command = "NORMAL"

            # Collect EAR values when eyes are open
            if EAR > 0.25:

                open_eye_values.append(EAR)

            cv2.putText(
                frame,
                f"Calibrating: {len(open_eye_values)}/{calibration_frames}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 0),
                2
            )

            if len(open_eye_values) >= calibration_frames:

                baseline = sum(open_eye_values) / len(open_eye_values)

                EAR_THRESHOLD = baseline * 0.75

                calibration_complete = True

                print("Calibration complete!")

                print(f"Baseline: {baseline:.3f}")

                print(f"Threshold: {EAR_THRESHOLD:.3f}")


        # ====================================================
        # 13. AFTER CALIBRATION
        # ====================================================

        else:

            # -----------------------------------------------
            # EYE CLOSED
            # -----------------------------------------------

            if EAR < EAR_THRESHOLD:

                closed_frame_count += 1

            else:

                closed_frame_count = 0

                prolonged_closure_detected = False


            # -----------------------------------------------
            # PROLONGED CLOSURE
            # -----------------------------------------------

            if closed_frame_count >= CLOSED_FRAME_LIMIT:

                prolonged_closure_detected = True


            # =================================================
            # 14. ESP32 ALERT
            # =================================================

            if prolonged_closure_detected:

                cv2.putText(
                    frame,
                    "DROWSINESS ALERT!",
                    (20, 250),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                    (0, 0, 0),
                    3
                )

                # Send only once
                if last_command != "ALERT":

                    esp32.write(
                        b"ALERT\n"
                    )

                    last_command = "ALERT"

            else:

                if last_command != "NORMAL":

                    esp32.write(
                        b"NORMAL\n"
                    )

                    last_command = "NORMAL"


        # ====================================================
        # 15. DISPLAY EAR
        # ====================================================

        cv2.putText(
            frame,
            f"EAR: {EAR:.3f}",
            (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 0),
            2
        )


        # ====================================================
        # 16. DISPLAY THRESHOLD
        # ====================================================

        if calibration_complete:

            cv2.putText(
                frame,
                f"Threshold: {EAR_THRESHOLD:.3f}",
                (20, 115),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 0),
                2
            )


        # ====================================================
        # 17. DISPLAY CLOSURE COUNT
        # ====================================================

        cv2.putText(
            frame,
            f"Closed Frames: {closed_frame_count}",
            (20, 150),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 0),
            2
        )


       

        # ====================================================
        # DRAW EYE LANDMARK POINTS ONLY
        # ====================================================

        for start, end in LEFT_EYE:

            point1 = face_landmarks.landmark[start]

            x1 = int(point1.x * width)
            y1 = int(point1.y * height)

            cv2.circle(
                frame,
                (x1, y1),
                2,
                (255, 0, 0),
                -1
            )


        for start, end in RIGHT_EYE:

            point1 = face_landmarks.landmark[start]

            x1 = int(point1.x * width)
            y1 = int(point1.y * height)

            cv2.circle(
                frame,
                (x1, y1),
                2,
                (255, 0, 0),
                -1
            )
    # ========================================================
    # 19. SHOW CAMERA
    # ========================================================

    cv2.imshow(
        "Eye Closure Detection",
        frame
    )


    # ========================================================
    # 20. QUIT
    # ========================================================

    if cv2.waitKey(1) & 0xFF == ord('q'):

        break


# ============================================================
# 21. CLEAN UP
# ============================================================

cap.release()

cv2.destroyAllWindows()

face_mesh.close()

esp32.close()
