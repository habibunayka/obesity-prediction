import streamlit as st
import pandas as pd
import pickle
import plotly.graph_objects as go

# Page configuration
st.set_page_config(page_title="Obesity Prediction", layout="centered")

st.markdown("""
    <style>
        body {
            background-color: #E0F7FA;
            background-image: url("https://via.placeholder.com/1500x1000.png"); /* Replace with your background image URL */
            background-size: cover;
        }
        .prediction-form, .result-table {
            background: rgba(255, 255, 255, 0.85);
            padding: 20px;
            border-radius: 10px;
            max-width: 700px;
            margin: auto;
        }
        .form-title {
            font-size: 36px;
            text-align: center;
            font-weight: bold;
        }
        .predict-button {
            display: flex;
            justify-content: center;
            margin-top: 20px;
        }
        .st-emotion-cache-1wivap2 {
            text-align: center !important;
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

# Initialize session state
if "page_number" not in st.session_state:
    st.session_state.page_number = 0
if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False
if "user_data" not in st.session_state:
    st.session_state.user_data = {}

# Show Start Page
def show_start_page():
    st.title("Obesity Prediction")
    st.write("Answer some questions to predict obesity risk. Click the button below to start.")
    if st.button("Start", on_click=lambda: st.session_state.update({"page_number": 1})):
        pass

# Display the question form based on the current page
def show_question_page():
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

    page_num = st.session_state.page_number
    question, options = questions[page_num - 1]

    st.subheader(question)
    if question in ["Age", "Height (in meters)", "Weight (in kg)", "Water intake (liters per day) (CH2O)", "Physical activity frequency (FAF)", "Time using technology devices (hours) (TUE)"]:
        user_input = st.number_input(f"Enter {question}", min_value=float(options[0]), max_value=float(options[-1]), step=0.01)
    else:
        user_input = st.selectbox(f"Select {question}", options)

    st.session_state.user_data[question] = user_input

    col1, col2 = st.columns(2)
    with col1:
        if page_num > 1:
            if st.button("Back", on_click=lambda: st.session_state.update({"page_number": page_num - 1})):
                pass
    with col2:
        if page_num < len(questions):
            if st.button("Next", on_click=lambda: st.session_state.update({"page_number": page_num + 1})):
                pass
        else:
            if st.button("Submit Quiz", on_click=lambda: st.session_state.update({"quiz_submitted": True})):
                pass

# Show prediction results
def show_prediction_results():
    st.subheader("PREDICTION RESULT")

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
    
    predictions_info = {
    "Obesity_Type_I": {
        "Tindakan Preventif": """
    - Tingkatkan Aktivitas Fisik: Usahakan untuk melakukan aktivitas fisik minimal 150 menit per minggu. Pilihlah aktivitas yang Anda nikmati, seperti berjalan kaki, bersepeda, atau berenang. Mulailah dengan intensitas ringan dan tingkatkan secara bertahap.
    - Porsi Makan yang Lebih Kecil: Gunakan piring yang lebih kecil untuk mengontrol porsi makan. Fokus pada makanan rendah kalori seperti sayuran, buah-buahan, dan protein tanpa lemak, serta hindari makanan tinggi gula dan lemak jenuh.
    """,
            "Tips Gaya Hidup": """
    - Olahraga Teratur: Cobalah untuk mengintegrasikan olahraga ke dalam rutinitas harian Anda. Misalnya, gunakan tangga daripada lift, atau berjalan kaki saat beristirahat.
    - Konsumsi Sayuran dan Buah: Usahakan untuk mengonsumsi setidaknya lima porsi sayuran dan buah setiap hari. Ini tidak hanya membantu mengontrol berat badan tetapi juga meningkatkan asupan serat dan nutrisi.
    """,
            "Saran Pemeriksaan": """
    - Konsultasi dengan Ahli Gizi: Temui ahli gizi untuk merancang rencana diet yang sesuai dengan kebutuhan pribadi Anda. 
    - Pemeriksaan Kesehatan Rutin: Lakukan pemeriksaan kesehatan setiap tahun untuk memantau kondisi jantung, tekanan darah, dan kadar kolesterol.
    """
        },
        "Obesity_Type_II": {
            "Tindakan Preventif": """
    - Perubahan Pola Makan yang Signifikan: Kurangi asupan gula, garam, dan lemak jenuh. Pilih makanan utuh seperti biji-bijian, protein tanpa lemak, dan lemak sehat dari sumber seperti alpukat dan kacang-kacangan.
    - Latihan Kekuatan: Sertakan latihan kekuatan minimal dua kali seminggu untuk membangun massa otot, yang dapat membantu meningkatkan metabolisme.
    """,
            "Tips Gaya Hidup": """
    - Program Penurunan Berat Badan: Pertimbangkan untuk bergabung dengan program penurunan berat badan yang terstruktur, seperti Weight Watchers atau program berbasis komunitas lainnya.
    - Hidrasi yang Cukup: Minumlah setidaknya 8 gelas air per hari. Air tidak hanya membantu mengontrol rasa lapar tetapi juga mendukung metabolisme yang sehat.
    """,
            "Saran Pemeriksaan": """
    - Pemeriksaan Kadar Gula Darah: Lakukan pemeriksaan kadar gula darah secara rutin untuk mendeteksi kemungkinan diabetes tipe 2.
    - Diskusi dengan Dokter: Bicarakan dengan dokter tentang kemungkinan penggunaan obat untuk membantu mengelola berat badan jika diperlukan.
    """
        },
        "Obesity_Type_III": {
            "Tindakan Preventif": """
    - Konsultasi Profesional Kesehatan: Segera temui dokter atau ahli gizi untuk mendapatkan rencana penurunan berat badan yang komprehensif dan aman, termasuk kemungkinan intervensi medis.
    - Perubahan Gaya Hidup yang Drastis: Fokus pada perubahan gaya hidup jangka panjang, bukan hanya penurunan berat badan sementara.
    """,
            "Tips Gaya Hidup": """
    - Dukungan dari Komunitas: Bergabunglah dengan kelompok dukungan penurunan berat badan untuk mendapatkan motivasi dan dukungan dari orang lain yang memiliki tujuan serupa.
    - Diet Sehat dan Terencana: Pertimbangkan untuk mengikuti pola makan yang lebih ketat, seperti diet Mediterania atau DASH, yang telah terbukti efektif dalam mengelola berat badan.
    """,
            "Saran Pemeriksaan": """
    - Pemeriksaan Kesehatan Menyeluruh: Lakukan pemeriksaan menyeluruh untuk menilai risiko penyakit terkait obesitas, seperti apnea tidur, hipertensi, dan masalah jantung.
    - Opsi Bedah Bariatrik: Diskusikan dengan dokter mengenai kemungkinan opsi bedah bariatrik jika penurunan berat badan dengan metode lain tidak berhasil.
    """
        },
        "Overweight_Level_I": {
            "Tindakan Preventif": """
    - Tingkatkan Aktivitas Fisik Secara Bertahap: Tambahkan aktivitas fisik ke dalam rutinitas harian Anda, seperti berjalan kaki selama 30 menit setiap hari.
    - Pengaturan Pola Makan: Fokus pada pengurangan makanan tinggi kalori dan lemak, serta pilih camilan sehat seperti buah, sayuran, atau kacang-kacangan.
    """,
            "Tips Gaya Hidup": """
    - Tujuan Penurunan Berat Badan: Tetapkan tujuan penurunan berat badan yang realistis, seperti 0,5-1 kg per minggu. Gunakan aplikasi pelacak kalori untuk membantu memantau asupan makanan.
    - Catatan Makanan: Buat catatan harian tentang apa yang Anda makan untuk meningkatkan kesadaran akan pola makan dan membantu mengidentifikasi kebiasaan buruk.
    """,
            "Saran Pemeriksaan": """
    - Pemeriksaan Kesehatan Tahunan: Lakukan pemeriksaan kesehatan tahunan untuk memantau berat badan, tekanan darah, dan kadar kolesterol.
    - Diskusi dengan Dokter: Bicarakan dengan dokter tentang strategi pencegahan untuk menghindari peningkatan berat badan lebih lanjut.
    """
        },
        "Overweight_Level_II": {
            "Tindakan Preventif": """
    - Diet Seimbang dan Olahraga Teratur: Fokus pada diet seimbang yang mencakup semua kelompok makanan dan lakukan olahraga minimal 300 menit per minggu.
    - Program Penurunan Berat Badan Terstruktur: Pertimbangkan untuk mengikuti program penurunan berat badan yang terstruktur untuk mendapatkan dukungan dan panduan.
    """,
            "Tips Gaya Hidup": """
    - Aktivitas Fisik yang Beragam: Cobalah berbagai jenis olahraga, seperti aerobik, yoga, atau kelas kebugaran, untuk menjaga motivasi dan minat.
    - Perhatikan Ukuran Porsi: Gunakan takaran makanan untuk membantu mengontrol porsi dan hindari makan berlebihan, terutama saat menonton TV atau menggunakan gadget.
    """,
            "Saran Pemeriksaan": """
    - Pemeriksaan Kadar Kolesterol dan Tekanan Darah: Lakukan pemeriksaan rutin untuk memantau kesehatan jantung dan risiko penyakit.
    - Konsultasi dengan Ahli Gizi: Diskusikan dengan ahli gizi untuk mendapatkan saran diet yang lebih spesifik dan sesuai dengan kebutuhan Anda.
    """
        },
        "Normal_Weight": {
            "Tindakan Preventif": """
    - Pertahankan Pola Makan Seimbang: Teruskan pola makan seimbang yang kaya akan sayuran, buah-buahan, biji-bijian, dan protein tanpa lemak untuk mencegah kenaikan berat badan.
    - Aktivitas Fisik yang Konsisten: Usahakan untuk tetap aktif dengan berbagai aktivitas fisik, seperti berolahraga, berkebun, atau berjalan kaki.
    """,
            "Tips Gaya Hidup": """
    - Hidrasi yang Cukup: Pastikan untuk minum cukup air setiap hari dan pilih camilan sehat seperti buah-buahan atau yogurt rendah lemak.
    - Pemantauan Berat Badan: Lakukan pemantauan berat badan secara berkala untuk memastikan tetap dalam rentang yang sehat.
    """,
            "Saran Pemeriksaan": """
    - Pemeriksaan Kesehatan Tahunan: Lakukan pemeriksaan kesehatan tahunan untuk memastikan kondisi kesehatan tetap baik dan mendeteksi masalah lebih awal.
    - Diskusi dengan Dokter: Bicarakan dengan dokter tentang cara menjaga berat badan yang sehat dan langkah-langkah pencegahan yang dapat diambil.
    """
        },
        "Insufficient_Weight": {
            "Tindakan Preventif": """
    - Tingkatkan Asupan Kalori: Pilih makanan yang kaya kalori dan bergizi, seperti alpukat, kacang-kacangan, dan produk susu penuh lemak.
    - Frekuensi Makan yang Lebih Tinggi: Cobalah untuk makan lebih sering, misalnya lima hingga enam kali sehari, dengan porsi yang lebih kecil.
    """,
            "Tips Gaya Hidup": """
    - Makanan Kaya Protein: Fokus pada makanan yang kaya protein, seperti daging tanpa lemak, ikan, telur, dan produk susu, untuk membantu meningkatkan massa otot.
    - Latihan Kekuatan: Sertakan latihan kekuatan dalam rutinitas Anda untuk membantu membangun massa otot dan meningkatkan berat badan.
    """,
            "Saran Pemeriksaan": """
    - Konsultasi dengan Ahli Gizi: Temui ahli gizi untuk mengevaluasi penyebab berat badan rendah dan mendapatkan rencana diet yang sesuai.
    - Pemeriksaan Kesehatan Menyeluruh: Lakukan pemeriksaan kesehatan untuk memastikan tidak ada kondisi medis yang mendasari yang menyebabkan berat badan rendah.
    """
        },
    }

    prediction = model.predict(pd.DataFrame([input_data]))

    # Menampilkan hasil prediksi
    st.metric(label="Obesity Prediction", value=f"{prediction[0]}")

    # Memastikan prediksi ada dalam dictionary info
    if prediction[0] in predictions_info:
        st.subheader(f"Informasi Kesehatan")
        for section, content in predictions_info[prediction[0]].items():
            st.write(f"**{section}:**")
            st.write(content)
    else:
        st.write("Hasil prediksi tidak ditemukan dalam daftar informasi yang tersedia.")

    # Menampilkan data input
    st.write("### Input Data:")
    result_df = pd.DataFrame.from_dict(input_data, orient='index', columns=["Value"])
    st.table(result_df)

    # Visualization
    # fig = go.Figure()
    # fig.add_trace(go.Scatter(x=result_df.index, y=result_df["Value"], mode='lines+markers', name="Input Features"))
    # fig.update_layout(title='Feature Progression for Obesity Prediction', xaxis_title='Features', yaxis_title='Values')
    # st.plotly_chart(fig)

# Main app logic
if st.session_state.quiz_submitted:
    show_prediction_results()
elif st.session_state.page_number == 0:
    show_start_page()
else:
    show_question_page()
