# Tests

Test scripts for Smart Annotator.

## Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test
python tests/test_platform_detection.py
```

## Available Tests

**Platform & Setup:**
- `test_platform_detection.py` - Platform detection and imports

**Core Features:**
- `test_auto_save.py` - Auto-save/load functionality
- `test_image_loading.py` - Image loading and navigation
- `test_annotation_labeling.py` - Label management

**Performance:**
- `test_performance_optimization.py` - Multi-annotation speed
- `test_memory_fix.py` - Memory leak detection
- `memory_leak_test.py` - Extended memory testing
- `comprehensive_memory_test.py` - Full memory analysis

**UI & Tools:**
- `test_gui_image_load.py` - GUI image loading
- `test_keyboard_shortcuts.py` - Keyboard shortcut system
- `test_brush_memory.py` - Brush tool memory usage
- `test_brightness_fix.py` - Image brightness handling

**Integration:**
- `test_with_images.py` - End-to-end with test images

## Test Requirements

Most tests run without PyQt5, but some GUI tests need:
```bash
pip install PyQt5==5.15.9
```

## Writing Tests

Keep tests simple:
1. Import what you need
2. Test one thing
3. Assert expected behavior
4. Clean up after yourself

Example:
```python
def test_feature():
    # Setup
    result = my_function(input_data)
    
    # Assert
    assert result == expected
```

## Test Data

Test images are in `data/test_images/` folder. Tests should not modify original data.

## CI/CD

Tests run automatically on:
- Push to main
- Pull requests
- Manual trigger

Check GitHub Actions for results.

---

Run tests before committing changes.
