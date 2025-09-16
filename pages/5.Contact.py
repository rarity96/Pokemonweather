from mainapp import st
from mainapp import send_email

st.write("If you have any idea for this project, or would like to work on front-end please let me know here")
mail_content = st.text_area("Message")
mail_back = st.text_input("Your email", key="input_emailpage")
if st.button("Send"):
    if not mail_content or not mail_content.strip():
        st.info("You cannot send empty message")
    else:
        try:
            send_email(mail_content, mail_back)
            st.success("The message has been sent successfully. Thanks for the feedback :)")
        except Exception as e:
            st.error(f"The message could not be sent: {e}")