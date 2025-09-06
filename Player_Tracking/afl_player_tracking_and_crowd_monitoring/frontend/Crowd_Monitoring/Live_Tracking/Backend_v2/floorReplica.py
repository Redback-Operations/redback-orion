import cv2
import numpy as np
import os

class FloorPlanAnnotator:
    def __init__(self, 
                 canvas_height=700, 
                 canvas_width=1000, 
                 tiles_x=25, 
                 tiles_y=15, 
                 background_image=None, 
                 show_grid=True):
        """
        Initialize a floor plan annotator
        
        Args:
            canvas_height (int): Height of the floor plan canvas
            canvas_width (int): Width of the floor plan canvas
            tiles_x (int): Number of tiles along x-axis
            tiles_y (int): Number of tiles along y-axis
            background_image (str/numpy.ndarray, optional): Path to image or image array to use as floor plan
            show_grid (bool): Whether to overlay grid lines on the floor plan
        """
        # Default floor plan image path
        default_floor_plan = os.path.join(
            os.path.dirname(__file__), 
            "/Users/apple/Desktop/Deakin/T2_2024/SIT764_Capstone/Crowd_Monitor/Stork Fountain.jpg"
        )
        
        self.canvas_height = canvas_height
        self.canvas_width = canvas_width
        self.tiles_x = tiles_x
        self.tiles_y = tiles_y
        self.show_grid = show_grid
        
        # Calculate tile dimensions
        self.tile_height = canvas_height // tiles_y
        self.tile_width = canvas_width // tiles_x
        
        # Determine background image
        if background_image is None:
            background_image = default_floor_plan
        
        # Load or create floor plan
        self.floor_image = self._load_or_create_floor_plan(background_image)
    
    def _load_or_create_floor_plan(self, background_image=None):
        """
        Load or create a floor plan image
        
        Args:
            background_image (str/numpy.ndarray, optional): Path to image or image array
        
        Returns:
            numpy.ndarray: Floor plan image
        """
        # If no background image provided, create a white canvas
        if background_image is None:
            floor_image = np.ones((self.canvas_height, self.canvas_width, 3), dtype=np.uint8) * 255
        else:
            # Load image from path or use provided array
            if isinstance(background_image, str):
                # Check if file exists
                if not os.path.exists(background_image):
                    print(f"Warning: Background image not found: {background_image}")
                    floor_image = np.ones((self.canvas_height, self.canvas_width, 3), dtype=np.uint8) * 255
                else:
                    # Read image
                    floor_image = cv2.imread(background_image)
                    
                    # Resize image to match canvas dimensions
                    floor_image = cv2.resize(floor_image, (self.canvas_width, self.canvas_height))
            elif isinstance(background_image, np.ndarray):
                # Resize provided image if needed
                floor_image = cv2.resize(background_image, (self.canvas_width, self.canvas_height))
            else:
                raise TypeError("Background image must be a file path or numpy array")
        
        # Add grid overlay if enabled
        if self.show_grid:
            for y in range(0, self.canvas_height, self.tile_height):
                for x in range(0, self.canvas_width, self.tile_width):
                    cv2.rectangle(floor_image, 
                                  (x, y), 
                                  (x + self.tile_width, y + self.tile_height), 
                                  (0, 0, 0), 1)
        
        return floor_image
    
    def annotate_trajectory(self, trajectory_points, color=(0, 0, 255), thickness=2):
        """
        Annotate a trajectory on the floor plan
        
        Args:
            trajectory_points (numpy.ndarray): Array of points representing trajectory
            color (tuple): Color of the trajectory line
            thickness (int): Thickness of the trajectory line
        
        Returns:
            numpy.ndarray: Annotated floor plan image
        """
        # Create a copy of the floor image to avoid modifying the original
        annotated_image = self.floor_image
        
        if len(trajectory_points) > 1:
            cv2.polylines(annotated_image, 
                          [trajectory_points.astype(np.int32)], 
                          isClosed=False, 
                          color=color, 
                          thickness=thickness)
        
        return annotated_image
    
    def get_floor_plan(self):
        """
        Get the current floor plan image
        
        Returns:
            numpy.ndarray: Floor plan image
        """
        return self.floor_image.copy()

    def update_floor_plan(self, new_background_image):
        """
        Update the floor plan with a new background image
        
        Args:
            new_background_image (str/numpy.ndarray): New background image
        """
        self.floor_image = self._load_or_create_floor_plan(new_background_image)

# Example usage
def main():
    # Try to load a custom floor plan image
    try:
        # Automatically find the image in the same directory
        current_dir = os.path.dirname(__file__)
        floor_plan_path = os.path.join(current_dir, "/Users/apple/Desktop/Deakin/T2_2024/SIT764_Capstone/Crowd_Monitor/Stork Fountain.jpg")
        
        floor_plan = FloorPlanAnnotator(
            background_image=floor_plan_path,
            show_grid=True  # Optional grid overlay
        )
        print(f"Loaded floor plan from: {floor_plan_path}")
    except Exception as e:
        print(f"Error loading floor plan image: {e}")

if __name__ == "__main__":
    main()