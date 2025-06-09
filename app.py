# app.py
import streamlit as st
import time
import random
import pandas as pd
#from fpdf import FPDF
from streamlit.components.v1 import html
from database import *

st.set_page_config(page_title="Vidyasagar",page_icon="🎓",layout="wide",initial_sidebar_state="expanded")

hide_st_style = """
   <style>
   #MainMenu {visibility: hidden;}
   footer {visibility: hidden;}
   header {visibility: hidden;}
   </style>
   """
st.markdown(hide_st_style, unsafe_allow_html=True)

init_db()

ADMIN_ID = "admin"
ADMIN_PASS = "admin123"

def admin_login():
    st.title("🔐 Admin Login")
    admin_id = st.text_input("Admin ID")
    admin_pass = st.text_input("Password", type="password")
    if st.button("Login"):
        if admin_id == ADMIN_ID and admin_pass == ADMIN_PASS:
            st.session_state.admin_authenticated = True
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid credentials")

def export_to_excel(students):
    df = pd.DataFrame(students, columns=["ID", "Name", "Submitted", "Score", "Time", "Semester"])
    df.to_excel("students.xlsx", index=False)
    st.download_button("📤 Export to Excel", data=open("students.xlsx", "rb"), file_name="students.xlsx")

#def export_to_pdf(students):
    #pdf = FPDF()
    #pdf.add_page()
    #pdf.set_font("Arial", size=12)
    #pdf.cell(200, 10, txt="Registered Students", ln=1, align="C")
    #for s in students:
       # pdf.cell(200, 10, txt=f"ID: {s[0]}, Name: {s[1]}, Score: {s[3]}, Time: {s[4]}, Semester: {s[5]}", ln=1)
    #pdf.output("students.pdf")
    #st.download_button("📤 Export to PDF", data=open("students.pdf", "rb"), file_name="students.pdf")

def admin_dashboard():
    st.title("🛠️ Admin Dashboard")
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Students", "➕ Add Questions", "❌ Delete Questions", "📝 Register Student", "🔁 Reset Student"])

    with tab1:
        st.subheader("Registered Students")
        sem_filter = st.selectbox("Select Semester to View Students", ["All", "1st", "2nd", "3rd", "4th", "5th", "6th"])
        students = get_all_students()
        if sem_filter != "All":
            students = [s for s in students if s[5] == sem_filter]
        st.info(f"Total Registered Students: {len(students)}")
        export_to_excel(students)
        export_to_pdf(students)
        for s in students:
            st.text(f"ID: {s[0]} | Name: {s[1]} | Score: {s[3]} | Time: {s[4]} | Semester: {s[5]}")
            if st.button(f"Delete {s[0]}"):
                delete_student(s[0])
                st.success(f"Deleted student {s[0]}")
                st.rerun()

    with tab2:
        st.subheader("Add MCQ Question")
        q = st.text_area("Question")
        o1 = st.text_input("Option 1")
        o2 = st.text_input("Option 2")
        o3 = st.text_input("Option 3")
        o4 = st.text_input("Option 4")
        ans = st.selectbox("Correct Answer", [o1, o2, o3, o4])
        semester = st.selectbox("Semester", ["1st", "2nd", "3rd", "4th", "5th", "6th"])
        if st.button("Add Question"):
            add_question(q, o1, o2, o3, o4, ans, semester)
            st.success("Question added")

    with tab3:
        st.subheader("Delete Questions")
        questions = get_all_questions()
        for q in questions:
            st.text(f"Q{q[0]}: {q[1]} (Semester: {q[2]})")
            if st.button(f"Delete Q{q[0]}"):
                delete_question(q[0])
                st.success(f"Deleted Q{q[0]}")
                st.rerun()

    with tab4:
        st.subheader("Register Student")
        reg_name = st.text_input("Student Name")
        reg_id = st.text_input("Student ID")
        semester = st.selectbox("Semester", ["1st", "2nd", "3rd", "4th", "5th", "6th"], key="semester_selectbox_1")

        if st.button("Register Student"):
            if reg_name and reg_id:
                if student_exists(reg_id):
                    st.error("Student ID already exists!")
                else:
                    register_student(reg_id, reg_name, semester)
                    st.success(f"Student {reg_name} ({reg_id}) registered successfully.")
            else:
                st.error("Please enter all fields.")

    with tab5:
        st.subheader("Reset Student Exam Status")
        sid = st.text_input("Enter Student ID to Reset")
        if st.button("Reset Student"):
            reset_student(sid)
            st.success(f"Reset exam attempt for Student ID: {sid}")

def exam_page():
    st.title("📘 Student Exam Portal")

    if not st.session_state.get("student_authenticated"):
        name = st.text_input("Enter Your Name")
        sid = st.text_input("Enter Your Unique Student ID")

        if st.button("Login"):
            result = verify_student(sid, name)
            if result is None:
                st.error("❌ You are not registered by the Office.")
            elif result[0] == 1:
                st.error("⚠️ You have already submitted the exam. Multiple attempts are not allowed.")
            else:
                st.session_state.student_authenticated = True
                st.session_state.sid = sid
                st.session_state.name = name
                st.session_state.semester = result[1]
                st.success("✅ Login successful. You can now start your exam.")
                st.rerun()
        return

    st.info(f"Welcome {st.session_state.name} ({st.session_state.sid})")

    if st.button("Start Exam") and not st.session_state.get("exam_started"):
        questions = get_all_questions_by_semester(st.session_state.semester)
        if not questions:
            st.warning("⚠️ No questions available for your semester.")
            return
        random.shuffle(questions)
        st.session_state.exam_started = True
        st.session_state.start_time = time.time()
        st.session_state.questions = questions
        st.session_state.answers = {}

    if st.session_state.get("exam_started"):
        
        html(
        '''
    <script>

    document.addEventListener('visibilitychange', function() {
      if (document.hidden) {
        alert("you switch the tab...You got one chance );
        let userName = prompt("waring code?");
        
        while (userName!=700636){
            alert("You Switch this tab! sorry you are not attemed this exam")
        }
        
      

      }
    });
  </script>

'''
    )

        
        st.warning("🚫 Do not switch tabs. Doing so will auto-submit the exam.")

        elapsed = time.time() - st.session_state.start_time
        remaining = 1500 - int(elapsed)
        st.warning(f"⏳ Time Remaining: {remaining//60}:{remaining%60:02d} mins")

        questions = st.session_state.get("questions", [])
        for q in questions:
            st.radio(f"{q[0]}. {q[1]}", [q[2], q[3], q[4], q[5]], key=f"q_{q[0]}")

        submitted_answers = {q[0]: st.session_state.get(f"q_{q[0]}") for q in questions}

        if remaining <= 0:
            st.session_state.exam_started = False
            score = sum(1 for q in questions if submitted_answers[q[0]] == q[6])
            submit_exam(st.session_state.sid, score)
            st.success(f"✅ Exam auto-submitted. Your Score: {score}")
            st.session_state.clear()
        elif st.button("Submit Now"):
            st.session_state.exam_started = False
            score = sum(1 for q in questions if submitted_answers[q[0]] == q[6])
            submit_exam(st.session_state.sid, score)
            st.success(f"✅ Exam submitted.")
            st.session_state.clear()

def main():
    menu = ["Student Exam", "Admin"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Admin":
        if not st.session_state.get("admin_authenticated"):
            admin_login()
        else:
            admin_dashboard()
    else:
        exam_page()
        st.header(":red[welcome] to exam page")


if __name__ == '__main__':
    main()
