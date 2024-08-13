import cv2
import mediapipe as mp
import pygame
import threading

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)


# Initialize MediaPipe Drawing
mp_drawing = mp.solutions.drawing_utils

# Initialize Pygame mixer
pygame.mixer.init()

# Preload audio files for each segment
segment_sounds = {
    "Segment 1": pygame.mixer.Sound('AudioNotes/f4.wav'),
    "Segment 2": pygame.mixer.Sound('AudioNotes/a4.wav'),
    "Segment 3": pygame.mixer.Sound('AudioNotes/g4.wav'),
    "Segment 4": pygame.mixer.Sound('AudioNotes/e4.wav'),
    "Segment 5": pygame.mixer.Sound('AudioNotes/d4.wav'),
    "Segment 6": pygame.mixer.Sound('AudioNotes/a3.wav'),
    "Segment 7": pygame.mixer.Sound('AudioNotes/d3.wav'),
    "Segment 8": pygame.mixer.Sound('AudioNotes/c4.wav')
}

# Start capturing video from webcam
cap = cv2.VideoCapture(0)

# Dictionary to store previous wrist positions, times, and cooldown states for each hand
previous_wrist_positions = {
    "Left": None,
    "Right": None
}
cooldown_active = {
    "Left": False,
    "Right": False
}
cooldown_time = 0.2  # 200 milliseconds cooldown between hits for each hand

threshold = 10 # Define a threshold for drastic downward movement
max_distance = 40  # Adjusted max distance for higher sensitivity

# Dictionary to track the color of each segment's circle
segment_colors = {
    "Segment 1": (255, 255, 255),
    "Segment 2": (255, 255, 255),
    "Segment 3": (255, 255, 255),
    "Segment 4": (255, 255, 255),
    "Segment 5": (255, 255, 255),
    "Segment 6": (255, 255, 255),
    "Segment 7": (255, 255, 255),
    "Segment 8": (255, 255, 255)
}

# Function to reset the color of the segment circle after a hit
def reset_segment_color(segment):
    segment_colors[segment] = (255, 255, 255)  # Reset to white

# Function to map distance to volume
def map_distance_to_volume(distance, min_distance=0, max_distance=max_distance):
    distance = max(min_distance, min(max_distance, distance))
    volume = (distance - min_distance) / (max_distance - min_distance)
    return volume

# Function to play audio with volume on a separate channel
def play_audio(segment, volume):
    channel = pygame.mixer.find_channel(True)  # Find an available channel
    if channel:
        channel.set_volume(volume)
        channel.play(segment_sounds[segment])

while True:
    # Read a frame from the webcam
    success, image = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        continue

    # Flip the image horizontally for a later selfie-view display
    image = cv2.flip(image, 1)

    # Resize the image to a lower resolution for faster processing
    image_resized = cv2.resize(image, (320, 240))
    
    # Convert the resized image to RGB
    image_rgb = cv2.cvtColor(image_resized, cv2.COLOR_BGR2RGB)

    # Process the image and find hands
    results = hands.process(image_rgb)

    # Get the width and height of the image
    image_width = image.shape[1]
    image_height = image.shape[0]

    # Calculate the maximum radius that fits within the grid
    horizontal_spacing = image_width / 4  # There are 4 horizontal segments
    vertical_spacing = image_height / 4  # There are 4 vertical segments (adjusted to match OpenCV's coordinate system)
    circle_radius = int(min(horizontal_spacing, vertical_spacing) * 0.9)  # Increase the radius to 90%

    # Define the center points for the segments with increased spacing
    segment_centers = [
        (int(image_width * 0.12), int(image_height * 0.25)),   # Segment 1
        (int(image_width * 0.375), int(image_height * 0.25)),   # Segment 2
        (int(image_width * 0.625), int(image_height * 0.25)),   # Segment 3
        (int(image_width * 0.88), int(image_height * 0.25)),    # Segment 4
        (int(image_width * 0.12), int(image_height * 0.75)),    # Segment 5
        (int(image_width * 0.375), int(image_height * 0.75)),   # Segment 6
        (int(image_width * 0.625), int(image_height * 0.75)),   # Segment 7
        (int(image_width * 0.88), int(image_height * 0.75))     # Segment 8
    ]

    # Define the letters to display in each segment
    segment_labels = ['F4', 'A4', 'G4', 'E4', 'D4', 'A3', 'D3', 'C4']

    # Draw larger white stroked circles for each segment and add text
    for i, center in enumerate(segment_centers):
        segment_name = f"Segment {i+1}"
        cv2.circle(image, center, circle_radius, segment_colors[segment_name], 2)  # Draw circle with the current color
        # Add text in the center of the circle
        cv2.putText(image, segment_labels[i], 
                    (center[0] - 10, center[1] + 10),  # Adjusted position for centering text
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    1,  # Font scale
                    segment_colors[segment_name],  # Use the current color for text
                    2,  # Thickness
                    cv2.LINE_AA)  # Anti-aliased line


    # Check if any hands are found
    if results.multi_hand_landmarks:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            # Get the label for the hand (Left or Right)
            label = handedness.classification[0].label

            # Get the y and x coordinates of the wrist landmark
            wrist_y = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].y * image_height
            wrist_x = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].x * image_width

            # Determine which segment the wrist is in
            if wrist_x < image_width * 0.25:
                segment = "Segment 1" if wrist_y < image_height * 0.5 else "Segment 5"
            elif wrist_x < image_width * 0.5:
                segment = "Segment 2" if wrist_y < image_height * 0.5 else "Segment 6"
            elif wrist_x < image_width * 0.75:
                segment = "Segment 3" if wrist_y < image_height * 0.5 else "Segment 7"
            else:
                segment = "Segment 4" if wrist_y < image_height * 0.5 else "Segment 8"

            # Check for drastic downward movement for the specific hand
            if previous_wrist_positions[label] is not None:
                distance_traveled = wrist_y - previous_wrist_positions[label]

                # Only register a hit if the wrist has moved downwards and the hand is not on cooldown
                if distance_traveled > threshold and not cooldown_active[label]:
                    # Map distance to volume and play audio only on hit detection
                    volume = map_distance_to_volume(distance_traveled)
                    print(f"{label} hand hit the drum in {segment} with distance {distance_traveled}! Volume: {volume}")
                    # Play the corresponding audio file with volume
                    play_audio(segment, volume)

                    # Change the color of the hit segment to black
                    segment_colors[segment] = (0, 0, 0)

                    # Reset the color back to white after 0.5 seconds
                    threading.Timer(0.5, reset_segment_color, args=[segment]).start()

                    # Activate cooldown for the specific hand
                    cooldown_active[label] = True

                    # Deactivate cooldown after cooldown_time
                    threading.Timer(cooldown_time, lambda hand=label: cooldown_active.update({hand: False})).start()

            # Update the previous position
            previous_wrist_positions[label] = wrist_y

    # Show the image with hand tracking
    cv2.imshow("Hand Tracking", image)

    # Break the loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close windows
cap.release()
cv2.destroyAllWindows()

# Quit Pygame mixer
pygame.mixer.quit()
