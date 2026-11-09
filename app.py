
import streamlit as st
import pandas as pd
import numpy as np
import pickle
import sqlite3
import hashlib
import os
from datetime import datetime

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="Laptop Price Predictor",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")
DB_PATH = os.path.join(BASE_DIR, "users.db")

CATEGORICAL_COLUMNS = [
    "Company", "TypeName", "Cpu", "Ram", "Gpu", "OpSys"
]

NUMERICAL_COLUMNS = ["Inches", "Weight"]


# ---------------- DARK THEME ----------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #0B1020;
    color: #F8FAFC;
}

[data-testid="stSidebar"] {
    background: #080D19;
    border-right: 1px solid #202A3D;
}

[data-testid="stSidebar"] * {
    color: #E2E8F0;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1450px;
}

h1, h2, h3 {
    color: #F8FAFC !important;
    font-weight: 700 !important;
}

p, label {
    color: #CBD5E1;
}

[data-testid="stMetric"] {
    background: #151F32;
    padding: 22px;
    border: 1px solid #26334A;
    border-radius: 15px;
}

[data-testid="stMetricLabel"] {
    color: #94A3B8 !important;
}

[data-testid="stMetricValue"] {
    color: #FFFFFF !important;
}

.stButton button, .stFormSubmitButton button {
    background: linear-gradient(90deg, #7C3AED, #8B5CF6);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 10px 20px;
    font-weight: 600;
    transition: 0.2s;
}

.stButton button:hover, .stFormSubmitButton button:hover {
    background: #6D28D9;
    color: white;
    border: none;
}

.stTextInput input, .stNumberInput input {
    background: #151F32 !important;
    color: white !important;
    border: 1px solid #334155 !important;
    border-radius: 9px !important;
}

.stSelectbox div[data-baseweb="select"] > div {
    background: #151F32;
    border-color: #334155;
    border-radius: 9px;
    color: white;
}

div[data-testid="stForm"] {
    background: #151F32;
    border: 1px solid #26334A;
    border-radius: 15px;
    padding: 25px;
}

.hero {
    background: linear-gradient(120deg, #171B3A, #172B42);
    border: 1px solid #34365E;
    border-radius: 20px;
    padding: 30px;
    margin-bottom: 25px;
}

.hero h1 {
    font-size: 32px;
    margin-bottom: 8px;
}

.hero p {
    color: #B6C2D5;
    font-size: 15px;
}

.result-card {
    background: linear-gradient(120deg, #211B49, #142D3B);
    border: 1px solid #6550A5;
    border-radius: 18px;
    padding: 28px;
    margin-top: 20px;
}

.result-price {
    font-size: 38px;
    font-weight: 800;
    color: #C4B5FD;
    margin-top: 10px;
}

.small-muted {
    color: #94A3B8;
    font-size: 13px;
}

.brand {
    font-size: 24px;
    font-weight: 800;
    color: #A78BFA;
    padding: 10px 0 25px 0;
}

hr {
    border-color: #26334A;
}
</style>
""", unsafe_allow_html=True)


# ---------------- DATABASE ----------------

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS app_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS app_predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            company TEXT,
            laptop_type TEXT,
            processor TEXT,
            ram TEXT,
            gpu TEXT,
            operating_system TEXT,
            inches REAL,
            weight REAL,
            predicted_price REAL,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def signup(username, email, password):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO app_users (username, email, password)
            VALUES (?, ?, ?)
        """, (username, email, hash_password(password)))

        conn.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        conn.close()


def login(email, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, username
        FROM app_users
        WHERE email=? AND password=?
    """, (email, hash_password(password)))

    user = cursor.fetchone()
    conn.close()

    return user


def save_prediction(user_id, values, price):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO app_predictions (
            user_id, company, laptop_type, processor, ram,
            gpu, operating_system, inches, weight,
            predicted_price, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        str(values["Company"]),
        str(values["TypeName"]),
        str(values["Cpu"]),
        str(values["Ram"]),
        str(values["Gpu"]),
        str(values["OpSys"]),
        float(values["Inches"]),
        float(values["Weight"]),
        float(price),
        datetime.now().strftime("%Y-%m-%d %H:%M")
    ))

    conn.commit()
    conn.close()


def get_history(user_id):
    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT
            company AS Company,
            laptop_type AS Type,
            processor AS Processor,
            ram AS RAM,
            gpu AS GPU,
            operating_system AS OS,
            inches AS Inches,
            weight AS Weight,
            predicted_price AS Price,
            created_at AS Date
        FROM app_predictions
        WHERE user_id=?
        ORDER BY id DESC
    """, conn, params=(user_id,))

    conn.close()
    return df


# ---------------- LOAD MODEL ----------------

@st.cache_resource
def load_model():
    with open(MODEL_PATH, "rb") as file:
        data = pickle.load(file)

    encoder = data["oneHotEncoder"]
    scaler = data["scaler"]
    model = data["model"]

    return encoder, scaler, model


# ---------------- MODEL FEATURE ORDER ----------------

def get_encoder_columns(encoder):
    if hasattr(encoder, "feature_names_in_"):
        return list(encoder.feature_names_in_)

    return CATEGORICAL_COLUMNS


def get_scaler_columns(scaler):
    if hasattr(scaler, "feature_names_in_"):
        return list(scaler.feature_names_in_)

    return NUMERICAL_COLUMNS


# ---------------- SESSION STATE ----------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "username" not in st.session_state:
    st.session_state.username = ""

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"


# ---------------- STARTUP ----------------

create_tables()

try:
    encoder, scaler, model = load_model()
    model_loaded = True
    model_error = ""

except Exception as e:
    model_loaded = False
    model_error = str(e)


# ---------------- AUTHENTICATION ----------------

def authentication_page():

    st.markdown("""
    <div class="hero">
        <h1>💻 Laptop Price Predictor</h1>
        <p>Smart machine learning. Better laptop price estimates.</p>
    </div>
    """, unsafe_allow_html=True)

    left, center, right = st.columns([1, 1.2, 1])

    with center:
        st.markdown("### Welcome")
        st.caption("Login to your account or create a new one.")

        login_tab, signup_tab = st.tabs(["Login", "Create Account"])

        with login_tab:
            with st.form("login_form"):
                email = st.text_input("Email Address")
                password = st.text_input("Password", type="password")

                submitted = st.form_submit_button(
                    "Login",
                    use_container_width=True
                )

                if submitted:
                    user = login(email.strip().lower(), password)

                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user_id = user[0]
                        st.session_state.username = user[1]
                        st.rerun()
                    else:
                        st.error("Incorrect email or password.")

        with signup_tab:
            with st.form("signup_form"):
                username = st.text_input("Username")
                email = st.text_input("Email Address")
                password = st.text_input("Password", type="password")
                confirm_password = st.text_input(
                    "Confirm Password",
                    type="password"
                )

                submitted = st.form_submit_button(
                    "Create Account",
                    use_container_width=True
                )

                if submitted:
                    if not username or not email or not password:
                        st.warning("Please complete all fields.")

                    elif password != confirm_password:
                        st.error("Passwords do not match.")

                    elif len(password) < 6:
                        st.warning("Password must contain at least 6 characters.")

                    else:
                        result = signup(
                            username.strip(),
                            email.strip().lower(),
                            password
                        )

                        if result:
                            st.success("Account created! You can now log in.")
                        else:
                            st.error("This email is already registered.")


# ---------------- DASHBOARD ----------------

def dashboard():

    history = get_history(st.session_state.user_id)

    total_predictions = len(history)

    average_price = history["Price"].mean() if total_predictions else 0
    latest_price = history.iloc[0]["Price"] if total_predictions else 0

    st.markdown(f"""
    <div class="hero">
        <h1>Welcome back, {st.session_state.username} 👋</h1>
        <p>Your laptop price prediction workspace.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Predictions", total_predictions)
    col2.metric("Average Predicted Price", f"€ {average_price:,.2f}")
    col3.metric("Latest Prediction", f"€ {latest_price:,.2f}")

    st.markdown("### Quick Actions")

    a, b = st.columns(2)

    with a:
        st.markdown("""
        <div class="result-card">
            <h3>💻 Predict Laptop Price</h3>
            <p>Enter laptop specifications and get an estimated price.</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Start Prediction", use_container_width=True):
            st.session_state.page = "Predict Price"
            st.rerun()

    with b:
        st.markdown("""
        <div class="result-card">
            <h3>📊 Prediction History</h3>
            <p>Review your previous laptop price predictions.</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("View History", use_container_width=True):
            st.session_state.page = "History"
            st.rerun()

    if total_predictions:
        st.markdown("### Recent Predictions")
        st.dataframe(
            history.head(5),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("You haven't made any predictions yet.")


# ---------------- PREDICTION PAGE ----------------

def prediction_page():

    st.title("💻 Laptop Price Prediction")
    st.caption("Enter the laptop specifications to estimate its price.")

    if not model_loaded:
        st.error("Model could not be loaded.")
        st.code(model_error)
        return

    encoder_columns = get_encoder_columns(encoder)
    scaler_columns = get_scaler_columns(scaler)

    # Check that the saved model has the expected input columns
    if set(encoder_columns) != set(CATEGORICAL_COLUMNS):
        st.error("The categorical columns in your saved encoder do not match this app.")
        st.write("Encoder columns:", encoder_columns)
        st.write("Expected columns:", CATEGORICAL_COLUMNS)
        return

    if set(scaler_columns) != set(NUMERICAL_COLUMNS):
        st.error("The numerical columns in your saved scaler do not match this app.")
        st.write("Scaler columns:", scaler_columns)
        st.write("Expected columns:", NUMERICAL_COLUMNS)
        return

    categories = {
        column: list(encoder.categories_[i])
        for i, column in enumerate(encoder_columns)
    }

    st.markdown("### Laptop Information")

    with st.form("prediction_form"):

        col1, col2 = st.columns(2)

        with col1:
            company = st.selectbox(
                "Company",
                categories["Company"],
                format_func=lambda x: str(x)
            )

            laptop_type = st.selectbox(
                "Laptop Type",
                categories["TypeName"],
                format_func=lambda x: str(x)
            )

            cpu = st.selectbox(
                "Processor",
                categories["Cpu"],
                format_func=lambda x: str(x)
            )

            ram = st.selectbox(
                "RAM",
                categories["Ram"],
                format_func=lambda x: str(x)
            )

        with col2:
            gpu = st.selectbox(
                "Graphics Card",
                categories["Gpu"],
                format_func=lambda x: str(x)
            )

            os_name = st.selectbox(
                "Operating System",
                categories["OpSys"],
                format_func=lambda x: str(x)
            )

            inches = st.number_input(
                "Screen Size (Inches)",
                min_value=10.0,
                max_value=20.0,
                value=15.6,
                step=0.1
            )

            weight = st.number_input(
                "Weight (kg)",
                min_value=0.5,
                max_value=5.0,
                value=1.8,
                step=0.1
            )

        submitted = st.form_submit_button(
            "✨ Predict Laptop Price",
            use_container_width=True
        )

    if submitted:

        try:
            # Keep original encoder category values and types
            categorical_values = {
                "Company": company,
                "TypeName": laptop_type,
                "Cpu": cpu,
                "Ram": ram,
                "Gpu": gpu,
                "OpSys": os_name
            }

            categorical_data = pd.DataFrame(
                [[categorical_values[col] for col in encoder_columns]],
                columns=encoder_columns
            )

            numerical_values = {
                "Inches": inches,
                "Weight": weight
            }

            numerical_data = pd.DataFrame(
                [[numerical_values[col] for col in scaler_columns]],
                columns=scaler_columns
            )

            # Apply the saved preprocessing
            encoded_data = encoder.transform(categorical_data)
            scaled_data = scaler.transform(numerical_data)

            # Support both sparse and dense encoder output
            if hasattr(encoded_data, "toarray"):
                encoded_data = encoded_data.toarray()

            final_data = np.concatenate(
                [scaled_data, encoded_data],
                axis=1
            )

            prediction = float(model.predict(final_data)[0])

            if not np.isfinite(prediction) or prediction <= 0:
                st.error("The model returned an invalid price. Check your input values.")
                return

            values = {
                **categorical_values,
                "Inches": inches,
                "Weight": weight
            }

            save_prediction(
                st.session_state.user_id,
                values,
                prediction
            )

            st.markdown(f"""
            <div class="result-card">
                <p class="small-muted">ESTIMATED LAPTOP PRICE</p>
                <div class="result-price">€ {prediction:,.2f}</div>
                <p>Prediction generated successfully.</p>
            </div>
            """, unsafe_allow_html=True)

            st.success("Your prediction has been saved to history.")

        except Exception as e:
            st.error("Prediction failed. Here is the exact error:")
            st.code(str(e))


# ---------------- HISTORY PAGE ----------------

def history_page():

    st.title("📚 Prediction History")
    st.caption("All your saved laptop price predictions.")

    history = get_history(st.session_state.user_id)

    if history.empty:
        st.info("No prediction history available yet.")
        return

    st.metric("Total Predictions", len(history))

    st.dataframe(
        history,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("### Price Trend")

    chart_data = history[["Date", "Price"]].copy()
    chart_data = chart_data.iloc[::-1]
    chart_data["Date"] = pd.to_datetime(chart_data["Date"])

    st.line_chart(
        chart_data.set_index("Date")["Price"]
    )


# ---------------- MODEL PERFORMANCE ----------------

def performance_page():

    st.title("📊 Model Performance")
    st.caption("Evaluation results from your test dataset.")

    col1, col2, col3 = st.columns(3)

    col1.metric("R² Score", "0.7175")
    col2.metric("MAE", "€ 13,352.79")
    col3.metric("RMSE", "€ 22,001.98")

    st.markdown("### Understanding the Results")

    st.markdown("""
    - **R² Score:** The model explains approximately 71.75% of the variation in laptop prices.
    - **MAE:** The average absolute prediction error is approximately €13,352.79.
    - **RMSE:** Larger prediction errors have more influence on this metric. Your RMSE is approximately €22,001.98.
    """)

    st.info(
        "These are your recorded test-set evaluation results. "
        "They are not a guarantee for every prediction."
    )

    st.markdown("### Model Information")
    st.write("**Algorithm:** Gradient Boosting Regressor")
    st.write("**Task:** Regression")
    st.write("**Target:** Laptop Price")
    st.write("**Evaluation:** R² Score, MAE and RMSE")


# ---------------- PROFILE PAGE ----------------

def profile_page():

    st.title("👤 My Profile")

    st.markdown("""
    <div class="result-card">
        <h3>Account Information</h3>
        <p class="small-muted">Your account details</p>
    </div>
    """, unsafe_allow_html=True)

    st.write("**Username:**", st.session_state.username)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT email FROM app_users WHERE id=?",
        (st.session_state.user_id,)
    )

    result = cursor.fetchone()
    conn.close()

    if result:
        st.write("**Email:**", result[0])

    st.markdown("---")
    st.caption("Laptop Price Predictor | Machine Learning Application")


# ---------------- MAIN APP ----------------

if not st.session_state.logged_in:

    authentication_page()

else:

    with st.sidebar:

        st.markdown(
            '<div class="brand">💻 LAPTOP AI</div>',
            unsafe_allow_html=True
        )

        st.caption("PRICE PREDICTION SYSTEM")
        st.markdown("---")

        st.write(f"Welcome, **{st.session_state.username}**")

        page = st.radio(
            "Navigation",
            [
                "Dashboard",
                "Predict Price",
                "History",
                "Model Performance",
                "Profile"
            ],
            key="navigation"
        )

        st.session_state.page = page

        st.markdown("---")

        if model_loaded:
            st.success("Model Connected")
        else:
            st.error("Model Not Connected")

        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_id = None
            st.session_state.username = ""
            st.session_state.page = "Dashboard"
            st.rerun()

    if st.session_state.page == "Dashboard":
        dashboard()

    elif st.session_state.page == "Predict Price":
        prediction_page()

    elif st.session_state.page == "History":
        history_page()

    elif st.session_state.page == "Model Performance":
        performance_page()

    elif st.session_state.page == "Profile":
        profile_page()
