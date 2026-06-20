# Smart Annotator Documentation

## Quick Start

```bash
conda activate ml
python main.py
```

## Managing Classes

Since GUI class management buttons may not work, use the script:

```bash
python data/manage_classes.py
```

Options:
1. View all classes
2. Add new class
3. Edit class
4. Remove class
5. Quick add multiple
6. Exit

## AI Tools

| Tool | Key | Usage |
|------|-----|-------|
| Magic Wand | 1 | Click on object |
| BBox Segment | 2 | Draw rectangle |
| Brush | 3 | Paint to refine |
| Auto Segment | 4 | Find all objects |
| Polygon | 5 | Manual polygon |
| Rectangle | 6 | Manual rectangle |

**Important**: Load an image first before using tools!

## Keyboard Shortcuts

- `Ctrl+O`: Load Image
- `Ctrl+S`: Save
- `Ctrl+E`: Export
- `1-6`: Select tools
- `Ctrl+Q`: Quit

## File Locations

- Labels: `data/label_classes.json`
- Auto-save: `data/auto_save/`
- Weights: `weights/sam/`, `weights/yolo/`

## Testing

```bash
python src/scripts/test_ai_tools.py
```
