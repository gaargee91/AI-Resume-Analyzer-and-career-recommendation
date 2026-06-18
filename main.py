import streamlit as st
import database as db

st.set_page_config(page_title= "AI Resume Analyzer", page_icon= "📃", layout = "wide")

db.create_tables()

st.markdown("""
<style>
div[data-baseweb= "tab-list"]{
justify-content: center;
margin-bottom: 2rem;
}
.stButton>button{
width: 100%;
border-radius: 8px;
background-color: #4F46E5;
color: white;
transition: all 0.3s ease;
}
.stButton>button:hover{
background-color: #4338CA;
transform: scale(1.02);
}
</style>
""", unsafe_allow_html=True)

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role =""
    

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>Welcome to the AI Resume Analyzer & Career Recommender📈🚀</h1>", unsafe_allow_html=True)
    
    st.markdown("<p style='text-align: center; color:#666;'>Upload your resume to get Ats scoring , skill gap analysis, and personalized career recommendation!</p>", unsafe_allow_html=True)

    st.write("")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        tab1, tab2 = st.tabs(["Log in" , "Sign Up"])

        with tab1:
            st.write("### Login to your account")
            login_user = st.text_input("Username", key="login_user")
            login_pass = st.text_input("Password", type="password", key="login_pass")
            
            if st.button("Login"):
                role = db.authentication_user(login_user, login_pass)
                if role:
                    st.session_state.logged_in = True
                    st.session_state.username = login_user
                    st.session_state.role = role
                    st.success(f"Welcome back, {login_user}!")
                    st.rerun()
                else:
                    st.error("Incorrect Username or Password")
                    
        with tab2:
            st.write("### Create a New Account")
            new_user = st.text_input("Choose a Username", key="reg_user")
            new_pass = st.text_input("Choose a Password", type="password", key="reg_pass")
            role_choice = st.selectbox("I am a:", ["Applicant", "Recruiter"])
            
            if st.button("Sign Up"):
                if new_user and new_pass:
                    success = db.add_user(new_user, new_pass, role_choice.lower())
                    if success:
                        st.success("Account created successfully! Please go to the Login tab.")
                    else:
                        st.error("Username already exists. Please choose another one.")
                else:
                    st.warning("Please fill in both fields.")   
                
else:
    st.sidebar.title(f"Welcome, {st.session_state.username}")
    st.sidebar.write(f"Role: {st.session_state.role.capitalize()}")
    st.sidebar.button("Logout", on_click=logout)

    st.title("Resume Analytics Dashboard📊")
