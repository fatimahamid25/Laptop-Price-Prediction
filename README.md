# 💻 Laptop Price Prediction System

### Machine Learning | Regression | Streamlit

A machine learning-based web application that predicts laptop prices based on their specifications. The system uses a trained machine learning model and an interactive Streamlit interface to provide estimated laptop prices.

---

## 📌 Project Overview

The **Laptop Price Prediction System** is a machine learning project developed to estimate laptop prices using available laptop specifications.

The project focuses on applying machine learning concepts to a real-world regression problem, including model training, prediction, data processing, and frontend integration.

Users can interact with the application, enter laptop information, and receive an estimated price.

## ✨ Key Features

- Laptop price prediction using a trained ML model.
- Interactive Streamlit dashboard.
- User-friendly prediction interface.
- Model integration using a saved `.pkl` file.
- User account and database functionality.
- Organized application structure.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming |
| Pandas | Data manipulation |
| NumPy | Numerical operations |
| Scikit-learn | Machine learning |
| Streamlit | Web application |
| Joblib / Pickle | Model loading |
| SQLite | Database management |

## ⚙️ Machine Learning Workflow

1. Dataset collection
2. Data cleaning and preprocessing
3. Feature preparation
4. Model training
5. Model evaluation
6. Model serialization
7. Streamlit application integration
8. Price prediction

## 📂 Project Structure

```text
Laptop-Price-Prediction/
│
├── app.py
├── database.py
├── model.pkl
├── requirements.txt
├── .gitignore
└── README.md
```

## 🚀 Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/fatimahamid25/Laptop-Price-Prediction.git
```

### 2. Navigate to the project folder

```bash
cd Laptop-Price-Prediction
```

### 3. Create a virtual environment

```bash
python -m venv .venv
```

### 4. Activate the environment

**Windows:**

```bash
.venv\Scripts\activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the application

```bash
streamlit run app.py
```

The application will open in your browser.

## 📊 Model Information

This project uses a pre-trained machine learning model stored in `model.pkl`.

The model is integrated into the Streamlit application to generate laptop price predictions from user-provided specifications.

## 🎯 Project Objectives

- Understand regression-based machine learning.
- Apply data preprocessing techniques.
- Develop a practical ML prediction system.
- Integrate a trained model with a web interface.
- Gain experience building end-to-end machine learning applications.

## 👩‍💻 Author

**Fatima Hamid**

GitHub: [@fatimahamid25](https://github.com/fatimahamid25)

---

*Developed as a Machine Learning project using Python.*
