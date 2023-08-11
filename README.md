# 🌳 bstree-tango: A Binary Search Tree Visualizer 🌳

**bstree-tango** is a Python-based project that visualizes binary search trees. Experience the interplay between algorithms and UI, brought to you by bstree-tango!

## Synopsis:
🌳 **Tango trees** are a type of _binary search tree (BST)_ introduced in computer science to optimize the number of rotations needed during search operations. 

💃The main idea behind **Tango** trees is to maintain a dynamic set of preferred paths within the tree and perform rotations to ensure that the searched item is always within these preferred paths.

## Demo (clickable screenshot):
[![Tango Trees Screenshot](https://github.com/StepanTita/bstree-tango/assets/44279105/3b54e10e-d84e-4a7d-8eec-28e72f1b4054)](https://www.youtube.com/watch?v=kwsRaTJJtiY "Tango Tree Demo")

## 🔍 Requirements:
- Python >= 3.6

## 📦 Setting Up:

1. **Install necessary packages:** The project requires several libraries which can be installed via pip. Here are the installation commands:

```bash
pip install pyautogui
pip install dash
pip install dash-html-components
pip install dash-core-components
pip install dash-table
```


For a step-by-step installation guide of Dash, please refer to the [official Dash installation documentation](https://dash.plot.ly/installation).

2. **Running the Program:** Once you've set up your environment, navigate to the directory containing `main.py` in your terminal or console and run the following command:
```bash
python main.py
```

❗️On the first run, the server might take a bit longer to start. Upon successful initiation, a local server address will appear. Copy and paste this address into your web browser to access the application.

## 🖥️ Testing:

- **Console Version:** To test the console version, navigate to `console/tree/tests` and run the `tester.py` file. This can be done either through the console (if Python is installed) or through any preferred IDE. There's a template within to guide you in creating test file names. The tester will alert you if search results don't match expectations. Test template format: count of numbers, range, actual numbers (sample tests are provided in the directory).

- **GUI Version:** For the version with a user interface, navigate to the `GUI` directory and run `main.py`. It's easiest to run this using PyCharm, which will handle the necessary setups for you.

## ⚠️ Notes:
- There seem to be issues deploying the project on Heroku due to missing event-driven libraries. Until resolved, deploying the project on Heroku may not be possible.

## License 📄

This project is licensed under the MIT License. See the [LICENSE.md](LICENSE.md) file for details.
