import cv2


def get_class_color(class_name): # Define specific colors for each class
    if class_name == "CAR":
        return (0, 0, 0)
    if class_name == "GCS":
        return (0, 0, 255)
    if class_name == "REF":
        return (0, 255, 0)


def draw_counts(frame, counts): # Draw the counts of each class on the frame
    text = f"CAR: {counts['CAR']}, GCS: {counts['GCS']}, REF: {counts['REF']}"

    font = cv2.FONT_HERSHEY_SIMPLEX # Use a simple font for the text
    font_scale = 0.7 # Set the font scale for better visibility
    thickness = 2 # Set the thickness of the text for better visibility

    text_size, _ = cv2.getTextSize(text, font, font_scale, thickness) #calculate the size of the text to position it correctly
    text_width, text_height = text_size # Get the width and height of the text to position it correctly

    x = frame.shape[1] - text_width - 20 # Position the text 20 pixels from the right edge of the frame
    y = frame.shape[0] - 20 # Position the text 20 pixels from the bottom edge of the frame

    cv2.putText( # Draw the text on the
        frame,
        text,
        (x, y),
        font,
        font_scale,
        (255, 255, 255),
        thickness
    )

    return frame


def draw_tracked_boxes(frame, result): # Draw bounding boxes and labels for tracked objects, and count the number of each class
    counts = {"CAR": 0, "GCS": 0, "REF": 0} # Initialize counts for each class

    if result.boxes is None: # If there are no boxes detected, just draw the counts on the frame
        frame = draw_counts(frame, counts)
        return frame

    names = result.names # Get the class names from the result object to map class IDs to class names

    for box in result.boxes: # Iterate through each detected box and draw it on the frame
        x1, y1, x2, y2 = box.xyxy[0].tolist() # Get the coordinates of the bounding box and convert them to integers for drawing
        cls_id = int(box.cls[0]) # Get the class ID of the detected object and convert it to an integer to map it to a class name   

        x1 = int(x1)
        y1 = int(y1)
        x2 = int(x2)
        y2 = int(y2)

        class_name = names[cls_id] # Map the class ID to a class name using the names list from the result object
        color = get_class_color(class_name) # Get the color for the class using the get_class_color function

        counts[class_name] += 1

        track_id = None # Initialize track_id to None, and if the box has an ID, set track_id to the integer value of the ID for labeling purposes
        if box.id is not None:
            track_id = int(box.id[0])

        if track_id is not None: # If track_id is available, include it in the label; otherwise, just use the class name for the label
            label = f"{class_name} ID:{track_id}"
        else:
            label = f"{class_name}"

        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2) # Draw the bounding box on the frame using the coordinates and color determined earlier
        cv2.putText(
            frame,
            label,
            (x1, max(20, y1 - 10)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            color,
            2
        )

    frame = draw_counts(frame, counts)
    return frame