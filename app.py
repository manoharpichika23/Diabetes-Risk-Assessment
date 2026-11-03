import streamlit as st
import pandas as pd
import joblib

from auth import register_user, login_user, logout_user


# =====================================
# PAGE CONFIGURATION
# =====================================

st.set_page_config(
    page_title="Diabetes AI | Risk Assessment",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =====================================
# SESSION STATE
# =====================================

DEFAULT_SESSION_VALUES = {
    "logged_in": False,
    "supabase": None,
    "user_id": None,
    "email": None,
    "pending_assessment": None,
    "pending_prediction": None,
    "pending_score": None,
}

for key, default_value in DEFAULT_SESSION_VALUES.items():
    if key not in st.session_state:
        st.session_state[key] = default_value


# =====================================
# CUSTOM UI / CSS
# =====================================

st.markdown(
    """
    <style>
    :root {
        --primary: #58A6FF;
        --surface: #171D29;
        --surface-light: #202938;
        --muted: #AAB7C4;
    }

    .stApp {
        background: linear-gradient(135deg, #0E1117 0%, #111827 100%);
    }

    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 2.5rem;
        max-width: 1500px;
    }

    h1, h2, h3 {
        letter-spacing: -0.4px;
    }

    h1 {
        color: #F3F7FC;
        font-weight: 750;
    }

    h2, h3 {
        color: #DCEBFA;
    }

    [data-testid="stSidebar"] {
        background: #171B27;
        border-right: 1px solid #293244;
    }

    [data-testid="stMetric"] {
        background: linear-gradient(145deg, #1B2636, #17202D);
        border: 1px solid #2D3B50;
        border-radius: 14px;
        padding: 16px 18px;
    }

    [data-testid="stMetricLabel"] {
        color: #AAB7C4;
    }

    [data-testid="stMetricValue"] {
        color: #69B4FF;
        font-weight: 750;
    }

    div.stButton > button,
    div.stFormSubmitButton > button {
        border-radius: 9px;
        min-height: 2.6rem;
        font-weight: 600;
    }

    div.stButton > button[kind="primary"],
    div.stFormSubmitButton > button[kind="primary"] {
        background: #1976D2;
        border: 1px solid #3194F4;
        color: white;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid #2D3B50;
        border-radius: 10px;
        overflow: hidden;
    }

    .hero-card {
        background: linear-gradient(115deg, #172A42, #1B2636);
        border: 1px solid #2E4B6B;
        border-radius: 16px;
        padding: 22px 24px;
        margin-bottom: 18px;
    }

    .hero-kicker {
        color: #80C1FF;
        font-size: 0.85rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .hero-title {
        color: #F5F9FF;
        font-size: 1.8rem;
        font-weight: 750;
        margin: 5px 0;
    }

    .hero-subtitle {
        color: #B8C8D9;
        margin-bottom: 0;
    }

    .section-note {
        color: #AAB7C4;
        font-size: 0.9rem;
    }

    .result-positive {
        background: #3A2028;
        border: 1px solid #8E3E4D;
        border-radius: 12px;
        padding: 16px;
    }

    .result-negative {
        background: #17382D;
        border: 1px solid #2F8061;
        border-radius: 12px;
        padding: 16px;
    }

    .small-muted {
        color: #AAB7C4;
        font-size: 0.82rem;
    }

    hr {
        border-color: #293244;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# =====================================
# HELPER FUNCTIONS
# =====================================

@st.cache_resource
def load_model():
    return joblib.load("diabetes_model.pkl")


def fetch_user_assessments():
    """Fetch assessment records belonging only to the logged-in user."""
    response = (
        st.session_state.supabase
        .table("assessment_history")
        .select(
            "id, created_at, pregnancies, glucose, blood_pressure, "
            "skin_thickness, insulin, bmi, "
            "diabetes_pedigree_function, age, prediction"
        )
        .eq("user_id", st.session_state.user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return response.data or []


# =====================================
# LOGIN AND REGISTRATION
# =====================================

if not st.session_state.logged_in:

    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-kicker">AI-powered health project</div>
            <div class="hero-title">🩺 Diabetes Risk Assessment</div>
            <p class="hero-subtitle">
                Sign in or create an account to access your personal
                assessment dashboard and saved history.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    auth_option = st.radio(
        "Choose an option",
        ["Login", "Register"],
        horizontal=True
    )

    if auth_option == "Register":

        st.subheader("Create Your Account")

        with st.form("register_form"):

            email = st.text_input("Email Address")

            password = st.text_input(
                "Password",
                type="password"
            )

            confirm_password = st.text_input(
                "Confirm Password",
                type="password"
            )

            register_submit = st.form_submit_button(
                "Create Account",
                use_container_width=True,
                type="primary"
            )

        if register_submit:

            if not email.strip() or not password:
                st.error("Please fill in all required fields.")

            elif password != confirm_password:
                st.error("Passwords do not match.")

            elif len(password) < 8:
                st.error("Password must contain at least 8 characters.")

            else:
                try:
                    response = register_user(
                        email.strip(),
                        password
                    )

                    if getattr(response, "session", None) is None:
                        st.success(
                            "Registration request successful. If email "
                            "confirmation is enabled in Supabase, confirm "
                            "your email before logging in."
                        )
                    else:
                        st.success(
                            "Account created successfully. You can now log in."
                        )

                except Exception as e:
                    st.error(f"Registration failed: {e}")

    else:

        st.subheader("Welcome Back")

        with st.form("login_form"):

            email = st.text_input("Email Address")

            password = st.text_input(
                "Password",
                type="password"
            )

            login_submit = st.form_submit_button(
                "Login",
                use_container_width=True,
                type="primary"
            )

        if login_submit:

            if not email.strip() or not password:
                st.error("Enter your email address and password.")

            else:
                try:
                    supabase, response = login_user(
                        email.strip(),
                        password
                    )

                    user = getattr(response, "user", None)
                    session = getattr(response, "session", None)

                    if user is None or session is None:
                        st.error(
                            "Login could not be completed. Check your "
                            "credentials and Supabase authentication settings."
                        )
                    else:
                        st.session_state.supabase = supabase
                        st.session_state.user_id = user.id
                        st.session_state.email = user.email
                        st.session_state.logged_in = True
                        st.rerun()

                except Exception as e:
                    st.error(f"Login failed: {e}")

    st.stop()


# =====================================
# LOAD MACHINE LEARNING MODEL
# =====================================

try:
    model = load_model()
except Exception as e:
    st.error(f"Unable to load diabetes_model.pkl: {e}")
    st.stop()


# =====================================
# SIDEBAR NAVIGATION
# =====================================

st.sidebar.markdown(
    """
    <div style="padding: 8px 0 14px 0;">
        <div style="font-size: 1.45rem; font-weight: 750; color: #F3F7FC;">
            🩺 Diabetes AI
        </div>
        <div style="color: #AAB7C4; font-size: 0.82rem; margin-top: 5px;">
            Risk Assessment System
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.divider()
st.sidebar.caption("SIGNED IN AS")
st.sidebar.write(st.session_state.email)

if st.sidebar.button("↪ Logout", use_container_width=True):

    try:
        if st.session_state.supabase is not None:
            logout_user(st.session_state.supabase)
    except Exception:
        pass
    finally:
        for key, default_value in DEFAULT_SESSION_VALUES.items():
            st.session_state[key] = default_value
        st.rerun()

st.sidebar.divider()

page = st.sidebar.radio(
    "MAIN MENU",
    [
        "Dashboard",
        "Risk Assessment",
        "Assessment History",
        "Health Guidance",
        "About Project"
    ]
)

st.sidebar.divider()
st.sidebar.caption("Educational prototype • Not for medical diagnosis")


# =====================================
# DASHBOARD
# =====================================

if page == "Dashboard":

    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-kicker">Personal overview</div>
            <div class="hero-title">Diabetes Risk Dashboard</div>
            <p class="hero-subtitle">
                Review your saved assessments and explore your model results.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    try:

        dashboard_records = fetch_user_assessments()

        total_assessments = len(dashboard_records)

        positive_count = sum(
            1 for record in dashboard_records
            if int(record.get("prediction", 0)) == 1
        )

        negative_count = sum(
            1 for record in dashboard_records
            if int(record.get("prediction", 0)) == 0
        )

        st.subheader("Your Assessment Overview")

        metric1, metric2, metric3, metric4 = st.columns(4)

        metric1.metric("Total Assessments", total_assessments)
        metric2.metric("Positive Classifications", positive_count)
        metric3.metric("Negative Classifications", negative_count)
        metric4.metric("Model Accuracy", "74.03%")

        st.caption(
            "Assessment counts are retrieved from Supabase for your account. "
            "Model accuracy is the reported test-set metric."
        )

        st.divider()
        st.subheader("Assessment Analytics")

        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:

            st.write("Your Prediction Distribution")

            if total_assessments:

                prediction_data = pd.DataFrame(
                    {
                        "Classification": ["Positive", "Negative"],
                        "Number of assessments": [
                            positive_count,
                            negative_count
                        ]
                    }
                )

                st.bar_chart(
                    prediction_data.set_index("Classification")
                )

            else:
                st.info(
                    "No saved assessments yet. Complete a risk assessment "
                                       "to populate this chart."
                )

        with chart_col2:

            st.write("Reported Model Performance")

            performance_data = pd.DataFrame(
                {
                    "Metric": [
                        "Accuracy",
                        "Precision",
                        "Recall",
                        "F1 Score",
                        "ROC-AUC"
                    ],
                    "Score": [
                        0.7403,
                        0.606,
                        0.741,
                        0.667,
                        0.818
                    ]
                }
            )

            st.bar_chart(
                performance_data.set_index("Metric")
            )

        st.divider()
        st.subheader("Recent Assessments")

        if dashboard_records:

            recent_df = pd.DataFrame(dashboard_records)

            recent_columns = [
                "created_at",
                "glucose",
                "blood_pressure",
                "bmi",
                "age",
                "prediction"
            ]

            st.dataframe(
                recent_df[recent_columns].head(5),
                use_container_width=True,
                hide_index=True
            )

            st.caption(
                "Prediction: 1 = positive class; 0 = negative class. "
                "These labels are model outputs, not a diagnosis."
            )

        else:

            st.info(
                "You have not saved any assessments yet. "
                "Open Risk Assessment to get started."
            )

    except Exception as e:
        st.error(f"Unable to load dashboard data: {e}")

    st.divider()
    st.subheader("Model Information")

    info1, info2, info3 = st.columns(3)

    info1.markdown("**Algorithm**  \nRandom Forest Classifier")
    info2.markdown("**Dataset**  \nPima Indians Diabetes Dataset")
    info3.markdown("**Optimization**  \nGridSearchCV")

    st.info(
        "The displayed performance metrics describe the model's reported "
        "held-out test results. They do not establish clinical reliability "
        "or suitability for diagnosis."
    )


# =====================================
# RISK ASSESSMENT
# =====================================

elif page == "Risk Assessment":

    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-kicker">Machine-learning assessment</div>
            <div class="hero-title">Risk Assessment</div>
            <p class="hero-subtitle">
                Enter the requested values to obtain an experimental
                model classification.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.form("diabetes_form"):

        st.subheader("Health Parameters")

        col1, col2 = st.columns(2)

        with col1:

            pregnancies = st.number_input(
                "Pregnancies",
                min_value=0,
                max_value=20,
                value=0,
                help="Number of times pregnant."
            )

            glucose = st.number_input(
                "Glucose Level",
                min_value=1,
                max_value=300,
                value=120,
                help="Enter the glucose value used by your dataset/model."
            )

            bp = st.number_input(
                "Blood Pressure",
                min_value=1,
                max_value=200,
                value=70
            )

            skin = st.number_input(
                "Skin Thickness",
                min_value=0,
                max_value=100,
                value=20
            )

        with col2:

            insulin = st.number_input(
                "Insulin",
                min_value=0,
                max_value=1000,
                value=80
            )

            bmi = st.number_input(
                "BMI",
                min_value=1.0,
                max_value=100.0,
                value=25.0,
                step=0.1
            )

            dpf = st.number_input(
                "Diabetes Pedigree Function",
                min_value=0.0,
                max_value=3.0,
                value=0.5,
                step=0.01
            )

            age = st.number_input(
                "Age",
                min_value=1,
                max_value=120,
                value=30
            )

        assess_submit = st.form_submit_button(
            "🧪 Assess Diabetes Risk",
            use_container_width=True,
            type="primary"
        )

    if assess_submit:

        input_data = pd.DataFrame(
            [[
                pregnancies,
                glucose,
                bp,
                skin,
                insulin,
                bmi,
                dpf,
                age
            ]],
            columns=[
                "Pregnancies",
                "Glucose",
                "BloodPressure",
                "SkinThickness",
                "Insulin",
                "BMI",
                "DiabetesPedigreeFunction",
                "Age"
            ]
        )

        try:

            prediction = int(model.predict(input_data)[0])
            positive_score = float(model.predict_proba(input_data)[0][1])

            st.session_state.pending_assessment = {
                "user_id": st.session_state.user_id,
                "pregnancies": int(pregnancies),
                "glucose": float(glucose),
                "blood_pressure": float(bp),
                "skin_thickness": float(skin),
                "insulin": float(insulin),
                "bmi": float(bmi),
                "diabetes_pedigree_function": float(dpf),
                "age": int(age),
                "prediction": prediction
            }

            st.session_state.pending_prediction = prediction
            st.session_state.pending_score = positive_score

        except Exception as e:
            st.error(f"Unable to generate prediction: {e}")

    # Display result outside the form so it remains visible after reruns.
    if st.session_state.pending_assessment is not None:

        st.divider()
        st.subheader("Assessment Result")

        prediction = st.session_state.pending_prediction
        score = st.session_state.pending_score

        if prediction == 1:

            st.markdown(
                """
                <div class="result-positive">
                    <strong>Positive class classification</strong><br>
                    <span class="small-muted">
                        The model assigned this input to the positive class.
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                """
                <div class="result-negative">
                    <strong>Negative class classification</strong><br>
                    <span class="small-muted">
                        The model assigned this input to the negative class.
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.write("")
        result_col1, result_col2 = st.columns(2)

        result_col1.metric(
            "Model Positive-Class Score",
            f"{score * 100:.2f}%"
        )

        result_col2.metric(
            "Predicted Class",
            "Positive (1)" if prediction == 1 else "Negative (0)"
        )

        st.caption(
            "The model score is not necessarily a calibrated probability "
            "of having diabetes."
        )

        st.warning(
            "This application is an educational prototype, not a medical "
            "diagnostic tool. A negative classification does not rule out "
            "diabetes. Consult a qualified healthcare professional for "
            "screening and interpretation."
        )

        if st.button(
            "💾 Save Assessment",
            use_container_width=True,
            type="primary",
            key="save_assessment_button"
        ):

            try:

                (
                    st.session_state.supabase
                    .table("assessment_history")
                    .insert(st.session_state.pending_assessment)
                    .execute()
                )

                st.success("Assessment saved successfully!")

                st.session_state.pending_assessment = None
                st.session_state.pending_prediction = None
                st.session_state.pending_score = None

            except Exception as e:
                st.error(f"Unable to save assessment: {e}")


# =====================================
# ASSESSMENT HISTORY
# =====================================

elif page == "Assessment History":

    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-kicker">Your saved records</div>
            <div class="hero-title">Assessment History</div>
            <p class="hero-subtitle">
                Search, filter and download your previous assessments.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    try:

        history = fetch_user_assessments()

        if history:

            history_df = pd.DataFrame(history)

            filter_col1, filter_col2 = st.columns([2, 1])

            with filter_col1:

                search_text = st.text_input(
                    "Search by glucose, BMI, age or date",
                    placeholder="Type a value to filter records..."
                )

            with filter_col2:

                prediction_filter = st.selectbox(
                    "Prediction filter",
                    [
                        "All",
                        "Positive class (1)",
                        "Negative class (0)"
                    ]
                )

            filtered_df = history_df.copy()

            if prediction_filter == "Positive class (1)":
                filtered_df = filtered_df[
                    filtered_df["prediction"].astype(int) == 1
                ]

            elif prediction_filter == "Negative class (0)":
                filtered_df = filtered_df[
                    filtered_df["prediction"].astype(int) == 0
                ]

            if search_text.strip():

                searchable = filtered_df.astype(str).apply(
                    lambda column: column.str.contains(
                        search_text.strip(),
                        case=False,
                        na=False
                    )
                ).any(axis=1)

                filtered_df = filtered_df[searchable]

            st.write(
                f"Showing **{len(filtered_df)}** of "
                f"**{len(history_df)}** saved assessments."
            )

            display_columns = [
                "created_at",
                "glucose",
                "blood_pressure",
                "bmi",
                "age",
                "prediction"
            ]

            st.dataframe(
                filtered_df[display_columns],
                use_container_width=True,
                hide_index=True
            )

            csv_data = filtered_df.to_csv(index=False).encode("utf-8")

            st.download_button(
                "⬇ Download assessments as CSV",
                data=csv_data,
                file_name="diabetes_assessment_history.csv",
                mime="text/csv",
                use_container_width=True
            )

            st.caption(
                "Prediction: 1 = positive class; 0 = negative class. "
                "The model classification is not a medical diagnosis."
            )

        else:

            st.info(
                "No previous assessments found. Complete and save "
                "a risk assessment to see it here."
            )

    except Exception as e:
        st.error(f"Unable to load assessment history: {e}")


# =====================================
# HEALTH GUIDANCE
# =====================================

elif page == "Health Guidance":

    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-kicker">Educational resources</div>
            <div class="hero-title">General Health Guidance</div>
            <p class="hero-subtitle">
                General information about healthy lifestyle habits
                and routine health screening.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    guidance_col1, guidance_col2 = st.columns(2)

    with guidance_col1:

        with st.expander("🥗 Healthy Eating", expanded=True):

            st.markdown(
                """
                - Include a variety of vegetables and fruits.
                - Choose balanced meals and high-fibre foods.
                - Limit sugary drinks and excess added sugar.
                - Follow advice suited to your individual health needs.
                """
            )

        with st.expander("🏃 Physical Activity"):

            st.markdown(
                """
                - Include regular physical activity as appropriate.
                - Walking and other suitable activities can be considered.
                - Avoid long periods of uninterrupted sitting.
                - Ask a healthcare professional about safe activity if needed.
                """
            )

    with guidance_col2:

        with st.expander("⚖️ Healthy Weight", expanded=True):

            st.markdown(
                """
                - Aim for sustainable, balanced eating habits.
                - Monitor health measurements appropriately.
                - Avoid extreme diets or unverified treatments.
                """
            )

        with st.expander("🩺 Regular Health Screening"):

            st.markdown(
                """
                - Discuss appropriate glucose screening with a clinician.
                - Follow up on abnormal laboratory results.
                - Share relevant family and health history with your clinician.
                """
            )

    st.warning(
        "This section provides general educational information only. "
        "It is not personalized medical advice and does not replace "
        "consultation with a healthcare professional."
    )


# =====================================
# ABOUT PROJECT
# =====================================

elif page == "About Project":

    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-kicker">Project information</div>
            <div class="hero-title">About Diabetes AI</div>
            <p class="hero-subtitle">
                AI-Powered Diabetes Risk Assessment and Management System
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.subheader("Project Overview")

    st.write(
        """
        This project uses a machine-learning classification model to
        analyze selected health-related input parameters and classify
        records into positive and negative diabetes classes.
        It provides an interactive Streamlit interface and stores
        user assessment history in Supabase.
        """
    )

    st.subheader("Technologies Used")

    tech1, tech2, tech3, tech4 = st.columns(4)

    tech1.info("**Python**\n\nCore programming language")
    tech2.info("**Scikit-learn**\n\nMachine-learning model")
    tech3.info("**Streamlit**\n\nInteractive web interface")
    tech4.info("**Supabase**\n\nAuthentication and database")

    st.subheader("Project Objectives")

    st.markdown(
        """
        1. Analyze selected health-related parameters.
        2. Develop a machine-learning classification model.
        3. Evaluate model performance on a test dataset.
        4. Provide an interactive assessment interface.
        5. Store and display each authenticated user's assessment history.
        """
    )

    st.info(
        "The project is an educational prototype. Its output should not "
        "be used to diagnose, treat or rule out diabetes."
    )
