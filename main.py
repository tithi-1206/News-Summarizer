import streamlit as st
import pandas as pd
import os
import hashlib
import logging 
from datetime import datetime

#file path for registering the users
file_path = 'registered_users.csv'


# Create the CSV file if it doesn't exist
if not os.path.exists(file_path):
    with open(file_path, 'w') as file:
        file.write('username,password\n')


#file path for logging the liked articles
log_file_path="D:\Fifth Sem\Advanced Python Project\like.log"


#logging info command
logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(message)s')


#the LOGIN function
def login(file_path):
    username = st.text_input("Username", key="username_input")
    password = st.text_input("Password", type="password", key="password_input")

    if st.button("Login"):
        with open(file_path, 'r') as file:
            lines = file.readlines()

        if len(lines) > 1:  # Check if there are any registered users (excluding header)
            user_data = [line.strip().split(",") for line in lines[1:]]

            for user in user_data:
                if user[0] == username and user[1] == password:
                    st.session_state.logged_in = True
                    st.session_state.username = username  # Store the username in the session state
                    st.success("Logged in as {}".format(username))
                    return True

            st.error("Incorrect username or password")
        else:
            st.error("No registered users found. Please register.")

    return False


#the REGISTER function
def register():
    new_username = st.text_input("Choose a username", key="new_username_input")
    new_password = st.text_input("Choose a password", type="password", key="new_password_input")

    if st.button("Register"):
        if new_username and new_password:
            with open(file_path, 'r') as file:
                lines = file.readlines()
            
            user_data = [line.strip().split(",") for line in lines[1:]] if len(lines) > 1 else []

            if any(user[0] == new_username for user in user_data):
                st.error("Username already exists. Please choose a different username.")
            else:
                with open(file_path, 'a') as file:
                    file.write(f"{new_username},{new_password}\n")
                st.success("Registration successful. You can now login.")
        else:
            st.warning("Please enter both username and password.")


#the function for LOGGING of LIKE BUTTON
def log_like_event(username, category):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_data = {'Username': [username], 'Category': [category], 'Timestamp': [timestamp]}
    log_df = pd.DataFrame(log_data)

    # Append to CSV file, create the file if it doesn't exist
    log_df.to_csv('like_log.csv', mode='a', header=not os.path.exists('like_log.csv'), index=False)


#the ENTERTAINMENT PAGE function
def entertainment_app():
    st.title("Entertainment News")
    st.write("Here's what going in the Entertainment Industry nowadays!")
    fetch_news("Entertainment")  # Get entertainment data

#the INDIA PAGE function
def india_app():
    st.title("India News")
    st.write("Here's what going on in India today!")
    fetch_news("India")  # Get India data

#the BUSINESS PAGE function
def business_app():
    st.title("Business News")
    st.write("Here's what Market has to say today!")
    fetch_news("Business")  # Get sports data

#the TECHNOLOGY PAGE function
def technology_app():
    st.title("Technology News")
    st.write("Here's what IT World has to show today!")
    fetch_news("Technology")  # Get technology data


#the function of FETCHING THE NEWS from the created csv files
def fetch_news(category):
    file_path = f"D:/News/{category}_Summarized.csv"
    try:
        news_data = pd.read_csv(file_path)  # Read CSV data using Pandas

        if not news_data.empty:  # Check if the DataFrame is not empty
            article_index = st.session_state.get('article_index', 0)

            if article_index < len(news_data):
                row = news_data.iloc[article_index]
                st.subheader(row.iloc[0])  # Display the heading
                st.write(row.iloc[1])  # Display the content

                if st.button("Next Article"):
                    article_index = (article_index + 1) % len(news_data)
                    st.session_state.article_index = article_index
            else:
                st.error("No more articles available.")
        else:
            st.error("No news data found for this category.")
    except FileNotFoundError:
        st.error("No news data found for this category.")


# Function to get file checksum
def file_checksum(file_path):
    with open(file_path, 'rb') as file:
        file_hash = hashlib.md5()
        while chunk := file.read(8192):
            file_hash.update(chunk)
    return file_hash.hexdigest()


# Function to update the Daily Trends chart
@st.cache_data
def update_chart():
    directory = 'D:/News'
    file_list = ['Entertainment_Summarized.csv', 'Business_Summarized.csv', 'Technology_Summarized.csv', 'India_Summarized.csv']

    category_counts = {}

    for file in file_list:
        file_path = os.path.join(directory, file)
        if os.path.exists(file_path):
            data = pd.read_csv(file_path)
            if file == 'Entertainment_Summarized.csv':
                file = 'Entertainment_News.csv'
            elif file == 'Business_Summarized.csv':
                file = 'Business_News.csv'
            elif file == 'Technology_Summarized.csv':
                file = 'Technology_News.csv'
            elif file == 'India_Summarized.csv':
                file = 'India_News.csv'
            
            category_counts[file.split('.')[0]] = len(data)

    if category_counts:
        counts_df = pd.DataFrame.from_dict(category_counts, orient='index', columns=['Count'])
        return counts_df
    else:
        return pd.DataFrame()

# Function to update the Your Daily Analysis chart
def display_first_chart():
    chart_data = pd.read_csv('like_log.csv', header=None)  # Read CSV file without headers
    if not chart_data.empty:
        st.bar_chart(chart_data[1].value_counts())  # Assuming the category is in the second column (index 1)
    else:
        st.error("No data available for the chart.")


# display Daily Trends Chart
def file_articles_chart():
    st.title('Daily Trends')
    st.write('Check out the Trends around the world!')
    
    chart_data = update_chart()  # Get the updated data

    # Display the bar chart
    st.bar_chart(chart_data)

    #st.experimental_rerun(interval=43200)

# display Your Daily Analysis Chart
def file_like_chart(username):
    st.title('Your Daily Analysis')
    st.write('Check out what you liked to read today')
    

    chart_data = pd.read_csv('like_log.csv', header=None)  # Skip headers by setting header=None
    user_likes = chart_data[chart_data[0] == username]  # Filter data for the specific user based on the first column index (0)

    if not user_likes.empty:
        st.bar_chart(user_likes[1].value_counts())  # Considering Category data in the second column (index 1)
    else:
        st.error("No data available for the chart.")


    #st.experimental_rerun(interval=60 * 60)

def set_background_image():
    st.image('https://t3.ftcdn.net/jpg/02/65/07/32/360_F_265073265_6RvGEh3TeKejn0cW4nhYjxJvHEmvC2Q9.jpg')

# MAIN code
def main():
    set_background_image()
    st.title("User Login and Registration")

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        selected_page = st.selectbox("Select an option", ["Signup", "Login"])
        
        if selected_page == "Login":
        
            st.subheader("Login")
            if login(file_path):
                st.session_state.logged_in = True
        else:
            st.subheader("Signup")
            register()

    if st.session_state.logged_in:
        st.subheader("Dashboard")
        
        # Get the user's choice for the dashboard
        selected_option = st.selectbox("Select an option", ["Entertainment", "India", "Business", "Technology", "Daily Trends","Your Daily Analysis"])

        # Based on the user's choice, display the respective dashboard
        if selected_option == "Entertainment":
            entertainment_app()
        elif selected_option == "India":
            india_app()
        elif selected_option == "Business":
            business_app()
        elif selected_option == "Technology":
            technology_app()
        elif selected_option == "Daily Trends":
            file_articles_chart()
        if selected_option == "Your Daily Analysis":
            file_like_chart(st.session_state.username)
        

        

        if selected_option in ["Entertainment", "Technology", "India", "Business"]:
            if st.button("Like"):
                log_like_event(st.session_state.username,selected_option)
                st.success(f"You liked the article in category '{selected_option}'!")


        if st.button("Logout"):
            st.session_state.logged_in = False
            st.info("You have been logged out.")

        if st.session_state.logged_in:
            last_update_time = st.session_state.get('last_update_time', '15 mins ago')
            st.text(f"Data last updated: {last_update_time}")
            #st.markdown("<style> p {font-size: 12px;}</style>", unsafe_allow_html=True)

# DRIVER code
if __name__ == "__main__":
    main()
    