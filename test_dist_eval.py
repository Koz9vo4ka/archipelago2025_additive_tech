import cv2
from typing import List
from numpy import ndarray, array


def calc_dist(x, a, b):
    return a / x + b


if __name__ == "__main__":
    """
    1 parrot - 166px
    2 parrot - 104px
    3 parot - 74px
    """
    
    def mask_image(frame: ndarray, lower_limit: List[int], higher_limit: List[int]) -> ndarray:
        frame_in_correct_color_scheme = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV_FULL)

        return cv2.inRange(frame_in_correct_color_scheme, array(lower_limit), array(higher_limit))


    def get_biggest_countur_width(binary: ndarray) -> float:
        contours = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[0]

        sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)

        if not sorted_contours: return

        biggest_contour = sorted_contours[0]

        x, y, w, h = cv2.boundingRect(biggest_contour)

        return w

    if True:
        while True:
            a, b = 3913.85, -6.93
            center_y = float(input())
            print(calc_dist(center_y, a, b))

    if False:
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("Error: Could not open webcam")
            exit()

        while True:
            # Capture frame-by-frame
            ret, frame = cap.read()

            # If frame is read correctly, ret is True
            if not ret:
                print("Error: Can't receive frame. Exiting...")
                break

            mask = mask_image(frame, [200, 50, 100], [360, 255, 255])
            width = get_biggest_countur_width(mask)
            dist = calc_dist(width, 266.89, -0.59)
            print(f"{dist = } {width = }")

            # Display the resulting frame
            cv2.imshow('Webcam Feed', frame)
            cv2.imshow('mask', mask)

            # Press 'q' to exit the loop
            if cv2.waitKey(1) == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
