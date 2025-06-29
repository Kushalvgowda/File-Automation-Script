# 📁 File Automation Script

A simple and efficient Python automation script that **automatically sorts files by extension into separate folders**. Integrated with a `.bat` file to run in the background and tested using `pytest` for reliability.

---

## 🚀 Features

- Automatically organizes files based on their extension (e.g., `.pdf`, `.txt`, `.jpg`)
- Creates folders dynamically if they don't exist
- Background execution using `.bat` file
- Tested with `pytest` for correctness

---

## 📂 How It Works

1. The Python script scans the target directory.
2. It identifies each file's extension.
3. It creates a new folder for each unique extension (if not already present).
4. Moves the file to the corresponding folder.
5. The `.bat` file runs the script silently in the background.

---

## 🛠️ Requirements

- Python 3.6+
- `pytest` (for testing)

```bash
pip install pytest
