#Hand tracking 
#References: MediaPipe libary 
import cv2
import mediapipe as mp
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

# For webcam input:
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
#Screen width and height
sw, sh = 640, 480 #cái này từ cái camera nếu đổi thành background thì lấy background heigh, width
cap.set(3,sw)
cap.set(4,sh)
with mp_hands.Hands(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as hands:
  while cap.isOpened():
    success, image = cap.read()
    if not success:
      print("Ignoring empty camera frame.")
      break
    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
    image.flags.writeable = False
    results = hands.process(image)
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    if results.multi_hand_landmarks:
      for hand_landmarks in results.multi_hand_landmarks:
        x, y = hand_landmarks.landmark[9].x*sw, hand_landmarks.landmark[9].y*sh
        x1,y1 = hand_landmarks.landmark[12].x*sw, hand_landmarks.landmark[12].y*sh

        cv2.circle(image,(int(x), int(y)), 10, (0,255,0), -1)
        cv2.circle(image,(int(x1), int(y1)), 10, (0,0,255), -1)

        if y1 > y:
            hand_status = "Closed"
        else:
            hand_status = "OPEN"
        
        cv2.putText(image, hand_status,(50,80), 0, 1.5, (0,0,255),2)

        mp_drawing.draw_landmarks(
            image,
            hand_landmarks,
            mp_hands.HAND_CONNECTIONS,
            mp_drawing_styles.get_default_hand_landmarks_style(),
            mp_drawing_styles.get_default_hand_connections_style())
    cv2.imshow('MediaPipe Hands', image) 
    if cv2.waitKey(5) & 0xFF == 27:
        break
cap.release()

