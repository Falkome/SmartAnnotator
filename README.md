# Smart Annotator
AI-Powered Image Annotation Tool with SAM (Segment Anything Model) and YOLO integration.

<p align="center">
  <img src="https://github.com/falkomeAI/SmartAnnotator/blob/main/data/demo.gif" width="600">
</p>


## Quick Start

```bash
python main.py
```

## Features

- **AI-Powered Segmentation**: SAM model for accurate object segmentation
- **Multiple Tools**: Magic Wand, BBox, Brush, Auto Segment, Polygon, Rectangle
- **Label Management**: Create, edit, and remove annotation classes
- **Auto-Save**: Automatic annotation saving
- **Export**: YOLO, COCO JSON, and mask formats

## Project Structure

```
smart-annotator/
├── data/           # Data files, images, scripts
├── models/         # AI model implementations
├── src/            # Core source code
├── ui/             # GUI components
├── weights/        # Model weights
├── main.py         # Main entry point
└── requirements.txt
```

## Usage
#### Weight File : [Downloads](https://drive.google.com/file/d/1J06bhKk0Hyp2hreEWwyKf0nD7IaSRSLX/view?usp=drive_link)
### 1. Run the Application
```bash
python main.py
```

### 2. Load an Image
- Click "📂 Load" button
- Or File → Load Image (Ctrl+O)

### 3. Select a Label
- Use the dropdown in Labels section (left panel)

### 4. Use AI Tools

| Tool | Key | Usage |
|------|-----|-------|
| Magic Wand | 1 | Click on object to segment |
| BBox Segment | 2 | Draw rectangle around object |
| Brush | 3 | Paint to refine segmentation |
| Auto Segment | 4 | Auto-detect all objects |
| Polygon | 5 | Draw manual polygon |
| Rectangle | 6 | Draw bounding box |

### 5. Save/Export
- File → Export Annotations (Ctrl+E)

## Managing Classes

To add, edit, or remove classes:

```bash
python data/manage_classes.py
```

This interactive script provides:
1. View all classes
2. Add new class
3. Edit class
4. Remove class
5. Quick add multiple classes

## Testing

```bash
python src/scripts/test_ai_tools.py
```

## Requirements

- Python 3.8+
- PyQt5
- OpenCV
- Ultralytics (SAM, YOLO)
- NumPy

Install dependencies:
```bash
pip install -r requirements.txt
```

## Keyboard Shortcuts

- `Ctrl+O`: Load Image
- `Ctrl+S`: Save
- `Ctrl+E`: Export
- `1-6`: Select tools
- `Ctrl+M`: Optimize memory
- `Ctrl+Q`: Quit

## File Locations

- **Labels**: `data/label_classes.json`
- **Auto-save**: `data/auto_save/`
- **SAM weights**: `weights/sam/`
- **YOLO weights**: `weights/yolo/`

## License

MIT License - See LICENSE file for details.
