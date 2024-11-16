import streamlit as st
import pandas as pd
import pickle
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(page_title="Obesity Prediction", layout="centered")

# Custom CSS for background styling
st.markdown("""
    <style>
        body {
            background-color: #E0F7FA;
            background-image: url("https://via.placeholder.com/1500x1000.png");
            background-size: cover;
        }
        .content {
            margin: 0 auto;
            padding: 20px;
            background-color: #ffffff;
            border-radius: 8px;
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
            max-width: 800px;
            color: black;
        }
        .form-title {
            font-size: 36px;
            text-align: center;
            font-weight: bold;
        }
        .form-content {
            background: rgba(255, 255, 255, 0.85);
            padding: 20px;
            border-radius: 10px;
            max-width: 700px;
            margin: auto;
        }
        .submit-btn {
            display: flex;
            justify-content: center;
            margin-top: 20px;
        }
        .result-table {
            background: rgba(255, 255, 255, 0.85);
            padding: 20px;
            border-radius: 10px;
            margin: auto;
            max-width: 800px;
        }
    </style>
""", unsafe_allow_html=True)

# Load the trained model
@st.cache_resource
def load_model():
    with open("models/obesity_model.pkl", "rb") as file:
        model = pickle.load(file)
    return model

model = load_model()

# Map function for CAEC and CALC inputs
def map_caec_calc(value):
    mapping = {'no': 3, 'Sometimes': 0, 'Frequently': 1, 'Always': 2}
    return mapping.get(value, 3)  # Default to 'no' if the value is unexpected

# Show Start Page
def show_start_page():
    st.markdown("<div class='form-title'>Obesity Prediction</div>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>Answer some questions that will appear to get obesity prediction results. Click the button below to start.</p>", unsafe_allow_html=True)
    if st.button("Start"):
        st.session_state.page_number = 1
        st.session_state.user_data = {}

# Display the question form based on the current page
def show_question_page(page_num):
    # Cek apakah quiz sudah disubmit
    if "quiz_submitted" in st.session_state and st.session_state.quiz_submitted:
        # Jika sudah disubmit, langsung tampilkan hasilnya
        return show_prediction_results()

    questions = [
        ("Gender", ["Male", "Female"]),
        ("Age", [str(i) for i in range(1, 121)]),
        ("Height (in meters)", [str(round(i, 2)) for i in [x / 100 for x in range(50, 251)]]),
        ("Weight (in kg)", [str(i) for i in range(10, 301)]),
        ("Family with Overweight", ["yes", "no"]),
        ("Do you eat high caloric food frequently? (FAVC)", ["yes", "no"]),
        ("How often do you eat vegetables? (FCVC)", ["1.0", "2.0", "3.0"]),
        ("Number of main meals (NCP)", ["1.0", "2.0", "3.0", "4.0"]),
        ("Consumption of food between meals? (CAEC)", ["no", "Sometimes", "Frequently", "Always"]),
        ("Do you smoke?", ["yes", "no"]),
        ("Water intake (liters per day) (CH2O)", ["1.0", "2.0", "3.0"]),
        ("Do you monitor calorie intake? (SCC)", ["yes", "no"]),
        ("Physical activity frequency (FAF)", ["0.0", "1.0", "2.0", "3.0"]),
        ("Time using technology devices (hours) (TUE)", ["0.0", "1.0", "2.0"]),
        ("Alcohol consumption frequency (CALC)", ["no", "Sometimes", "Frequently", "Always"]),
    ]

    question, options = questions[page_num - 1]

    st.markdown(f"<div class='form-title'>{question}</div>", unsafe_allow_html=True)
    if question in ["Age", "Height (in meters)", "Weight (in kg)", "Water intake (liters per day) (CH2O)", "Physical activity frequency (FAF)", "Time using technology devices (hours) (TUE)"]:
        user_input = st.number_input(f"Select {question}", min_value=float(options[0]), max_value=float(options[-1]), step=0.01)
    else:
        user_input = st.selectbox(f"Select {question}", options)
    
    st.session_state.user_data[question] = user_input

    if page_num < len(questions):
        if st.button("Next"):
            st.session_state.page_number += 1
    else:
        if st.button("Submit Quiz"):
            st.session_state.quiz_submitted = True  # Menandakan quiz sudah disubmit
            show_prediction_results()
# dg738
# Show prediction results
def show_prediction_results():
    st.markdown("<div class='form-title'>PREDICTION RESULT</div>", unsafe_allow_html=True)

    # Process inputs and make prediction
    input_data = {
        "Gender": 1 if st.session_state.user_data["Gender"] == "Male" else 0,
        "Age": int(st.session_state.user_data["Age"]),
        "Height": float(st.session_state.user_data["Height (in meters)"]),
        "Weight": float(st.session_state.user_data["Weight (in kg)"]),
        "family_history_with_overweight": 1 if st.session_state.user_data["Family with Overweight"] == "yes" else 0,
        "FAVC": 1 if st.session_state.user_data["Do you eat high caloric food frequently? (FAVC)"] == "yes" else 0,
        "FCVC": float(st.session_state.user_data["How often do you eat vegetables? (FCVC)"]),
        "NCP": float(st.session_state.user_data["Number of main meals (NCP)"]),
        "CAEC": map_caec_calc(st.session_state.user_data["Consumption of food between meals? (CAEC)"]),
        "SMOKE": 1 if st.session_state.user_data["Do you smoke?"] == "yes" else 0,
        "CH2O": float(st.session_state.user_data["Water intake (liters per day) (CH2O)"]),
        "SCC": 1 if st.session_state.user_data["Do you monitor calorie intake? (SCC)"] == "yes" else 0,
        "FAF": float(st.session_state.user_data["Physical activity frequency (FAF)"]),
        "TUE": float(st.session_state.user_data["Time using technology devices (hours) (TUE)"]),
        "CALC": map_caec_calc(st.session_state.user_data["Alcohol consumption frequency (CALC)"])
    }

    prediction = model.predict(pd.DataFrame([input_data]))

    # Display results
    st.markdown("<div class='result-table'>", unsafe_allow_html=True)
    result_df = pd.DataFrame.from_dict(input_data, orient='index', columns=["Value"])
    st.table(result_df)
    st.markdown("</div>", unsafe_allow_html=True)

    st.metric(label="Obesity Prediction", value=f"{prediction[0]}", delta="")

    # Visualization: Plotly chart example
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=result_df.index, y=result_df["Value"], mode='lines+markers', name="Input Features"))
    fig.update_layout(title='Feature Progression for Obesity Prediction', xaxis_title='Features', yaxis_title='Values')
    st.plotly_chart(fig)


# Main app logic
if "page_number" not in st.session_state:
    st.session_state.page_number = 0

if st.session_state.page_number == 0:
    show_start_page()
else:
    show_question_page(st.session_state.page_number)
