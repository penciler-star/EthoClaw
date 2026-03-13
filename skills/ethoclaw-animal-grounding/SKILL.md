---
name: ethoclaw-animal-grounding
description: Animal grounding (center tracking) using OpenCV for 2D top-view videos of black mice.
metadata:
  {
    "openclaw":
      {
        "emoji": "🐭",
        "requires": { "python": ["opencv-python", "numpy", "pandas"] },
        "install":
          [
            { "id": "pip", "kind": "pip", "package": "opencv-python", "label": "Install OpenCV" },
            { "id": "pip", "kind": "pip", "package": "numpy", "label": "Install NumPy" },
            { "id": "pip", "kind": "pip", "package": "pandas", "label": "Install Pandas" },
          ],
      },
  }
---

# Animal Grounding (Center Tracking)

Use OpenCV-based computer vision methods to track the body center position of black mice in 2D top-view videos. Results are saved in DeepLabCut compatible format.

## Algorithm Description

The tracking algorithm uses the following approach:

1. **Frame differencing**: Detect moving objects by comparing consecutive frames
2. **Contour detection**: Find contours of the detected motion regions
3. **Center calculation**: Calculate the centroid (center of mass) of the largest contour as the animal position
4. **Smoothing**: Apply simple moving average to reduce jitter

## Quick Start

### Analyze a Single Video

```python
import cv2
import numpy as np
import pandas as pd
from pathlib import Path
from collections import deque

def track_animal_center(video_path, output_folder=None, smoothing_window=5, visualize=True):
    """
    Track animal center position in a video using OpenCV.

    Args:
        video_path: Path to the video file
        output_folder: Output directory (default: same as video)
        smoothing_window: Window size for moving average smoothing
        visualize: Whether to generate tracking visualization video

    Returns:
        DataFrame with tracking results
    """

    # Determine output directory
    video_path = Path(video_path)
    if output_folder is None:
        output_folder = video_path.parent
    else:
        output_folder = Path(output_folder)
        output_folder.mkdir(parents=True, exist_ok=True)

    # Open video
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")

    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Initialize variables
    centers = []
    frame_indices = []
    smoothing_buffer = deque(maxlen=smoothing_window)

    # Background subtractor
    bg_subtractor = cv2.createBackgroundSubtractorMOG2(detectShadows=False)

    # Read first frame
    ret, prev_frame = cap.read()
    if not ret:
        raise ValueError("Cannot read first frame")

    frame_idx = 0

    # Initialize video writer for visualization
    if visualize:
        output_video_path = output_folder / f"{video_path.stem}_labeled.mp4"
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(output_video_path), fourcc, fps, (width, height))

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_idx += 1

        # Apply background subtraction
        fg_mask = bg_subtractor.apply(frame)

        # Apply threshold to get binary image
        _, thresh = cv2.threshold(fg_mask, 50, 255, cv2.THRESH_BINARY)

        # Morphological operations to remove noise
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            # Find the largest contour
            largest_contour = max(contours, key=cv2.contourArea)

            # Filter small contours (noise)
            if cv2.contourArea(largest_contour) > 500:
                # Calculate centroid
                M = cv2.moments(largest_contour)
                if M["m00"] > 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])

                    # Apply smoothing
                    smoothing_buffer.append((cx, cy))
                    smoothed_cx = int(np.mean([p[0] for p in smoothing_buffer]))
                    smoothed_cy = int(np.mean([p[1] for p in smoothing_buffer]))

                    centers.append([smoothed_cx, smoothed_cy, 1.0])  # [x, y, likelihood]
                else:
                    centers.append([cx, cy, 0.0] if 'cx' in locals() else [0, 0, 0.0])
            else:
                centers.append([0, 0, 0.0])
        else:
            centers.append([0, 0, 0.0])

        frame_indices.append(frame_idx)

        # Draw visualization
        if visualize:
            vis_frame = frame.copy()

            if centers[-1][2] > 0:
                cv2.circle(vis_frame, (centers[-1][0], centers[-1][1]), 10, (0, 255, 0), -1)
                cv2.putText(vis_frame, "center", (centers[-1][0] + 15, centers[-1][1] - 15),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            # Add frame number
            cv2.putText(vis_frame, f"Frame: {frame_idx}/{total_frames}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            out.write(vis_frame)

    # Release resources
    cap.release()
    if visualize:
        out.release()

    # Create DataFrame in DeepLabCut format
    # DeepLabCut format: multi-index columns (scorer, individual, bodypart, coord)
    n_frames = len(frame_indices)

    # Create multi-level column index
    columns = pd.MultiIndex.from_tuples([
        ('ethoclaw_animal_grounding', 'center', 'x', 'x'),
        ('ethoclaw_animal_grounding', 'center', 'x', 'y'),
        ('ethoclaw_animal_grounding', 'center', 'x', 'likelihood'),
    ], names=['scorer', 'individuals', 'bodyparts', 'coords'])

    # Create data array
    data = np.array(centers)
    df = pd.DataFrame(data, columns=columns, index=frame_indices)
    df.index.name = 'frames'

    # Save to CSV
    csv_path = output_folder / f"{video_path.stem}DLC_center.csv"
    df.to_csv(csv_path)

    # Save to H5
    h5_path = output_folder / f"{video_path.stem}DLC_center.h5"
    df.to_hdf(h5_path, key='df_with_missing', mode='w')

    print(f"Tracking complete!")
    print(f"Results saved to: {output_folder}")
    print(f"  - CSV: {csv_path.name}")
    print(f"  - H5: {h5_path.name}")
    if visualize:
        print(f"  - Video: {output_video_path.name}")

    return df


# ==================== User Configuration ====================

# Video path (Required)
video_path = "/path/to/your/video.mp4"

# Output directory (Optional, default: same as video)
output_folder = None  # Example: "/path/to/output"

# Smoothing window size (Optional, default: 5)
# Larger values = smoother but more lag
smoothing_window = 5

# Generate visualization video (Optional, default: True)
visualize = True

# ==================== Run Tracking ====================

df = track_animal_center(
    video_path=video_path,
    output_folder=output_folder,
    smoothing_window=smoothing_window,
    visualize=visualize
)
```

## Parameter Description

| Parameter          | Type | Default  | Description                                            |
| ------------------ | ---- | -------- | ------------------------------------------------------ |
| `video_path`       | str  | Required | Path to the video file                                 |
| `output_folder`    | str  | None     | Output directory, if None uses same directory as video |
| `smoothing_window` | int  | 5        | Window size for moving average smoothing               |
| `visualize`        | bool | True     | Whether to generate tracking visualization video       |

## Output Results

After analysis, the following files will be generated in the output directory:

- **`video_nameDLC_center.h5`**: HDF5 file containing tracking data in DeepLabCut format
- **`video_nameDLC_center.csv`**: CSV file containing tracking data (same content as H5)
- **`video_name_labeled.mp4`**: Visualization video with center point annotated

## Result Data Structure

The output CSV/H5 files follow DeepLabCut's format with multi-level columns:

- **scorer**: `ethoclaw_animal_grounding`
- **individuals**: `center`
- **bodyparts**: `center`
- **coords**: `x`, `y`, `likelihood`

Each row represents a frame, with the x, y coordinates and likelihood (1.0 for valid detection, 0.0 for no detection).

## Algorithm Details

### Background Subtraction

The algorithm uses OpenCV's MOG2 (Mixture of Gaussians) background subtractor to detect moving objects. This method models each pixel as a mixture of Gaussians and adapts to changes in the background.

### Contour Processing

- Detects external contours in the foreground mask
- Selects the largest contour as the animal (assumes single animal)
- Filters out small contours (area < 500 pixels) as noise

### Center Calculation

- Uses image moments to calculate the centroid of the contour
- Applies a moving average filter to reduce jitter between frames

## Notes

1. **Single Animal**: This algorithm assumes a single animal in the frame. For multiple animals, consider using DeepLabCut's pose estimation instead.

2. **Contrast Requirements**: Works best when the animal has good contrast with the background. For black mice on dark backgrounds, ensure adequate lighting.

3. **Frame Rate**: The tracking accuracy depends on the video frame rate. Higher frame rates provide smoother tracking.

4. **No Detection**: When no animal is detected (e.g., animal leaves frame), the center position is set to (0, 0) with likelihood 0.0.

5. **DeepLabCut Compatibility**: The output format is compatible with DeepLabCut's native format, allowing integration with other DeepLabCut analysis tools.
