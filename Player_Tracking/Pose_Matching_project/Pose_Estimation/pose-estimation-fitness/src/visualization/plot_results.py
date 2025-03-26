import matplotlib.pyplot as plt
import numpy as np

def plot_limb_positions(positions, title='Limb Positions', save_path=None):
    """
    Plots the limb positions during exercises and optionally saves the plot.
    """
    plt.figure(figsize=(10, 6))
    for limb, coords in positions.items():
        plt.scatter(coords[0], coords[1], label=limb)
        plt.plot(coords[0], coords[1], marker='o')
    plt.title(title)
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.grid()
    plt.legend()
    if save_path:
        plt.savefig(save_path)  # Save the plot
    plt.show()

def plot_strain_metrics(metrics, title='Strain Metrics'):
    """
    Plots strain metrics over time.
    """
    plt.figure(figsize=(10, 6))
    plt.plot(metrics, color='red', marker='o')
    plt.title(title)
    plt.xlabel('Time (frames)')
    plt.ylabel('Strain Value')
    plt.grid()
    plt.show()

def plot_results(pose_outputs, strain_results, limb_position_results):
    """
    Wrapper function to plot all results.
    """
    # Example: Call the existing plotting functions
    for i, pose in enumerate(pose_outputs):
        print(f"Pose {i + 1}: {pose}")
    plot_limb_positions(limb_position_results, title="Limb Positions")
    plot_strain_metrics(strain_results, title="Strain Metrics")