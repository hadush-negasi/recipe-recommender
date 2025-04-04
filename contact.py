import streamlit as st
from streamlit_extras.card import card
import requests
from email_validator import validate_email, EmailNotValidError

def app():
    # ---- Hero Section ----
    st.markdown(
        """
        <style>
        .hero-contact {
            background: linear-gradient(135deg, #2e8b57 0%, #3aafa9 100%);
            padding: 2.5rem;
            padding-bottom: 0px;
            border-radius: 15px;
            color: white;
            text-align: center;
            margin-bottom: 2.5rem;
        }
        .hero-contact h1 {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }
        </style>
        <div class="hero-contact">
            <h1>Get in Touch</h1>
            <p>We'd love to hear from you! Reach out for questions, feedback, or collaborations.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ---- Contact Cards Grid ----
    cols = st.columns(3)
    
    with cols[0]:
        card(
            title="Email Us",
            text="hadush7512@gmail.com",
            image="https://images.unsplash.com/photo-1498050108023-c5249f4df085?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=80",
            url="mailto:hadush7512@gmail.com",
            styles={
                "card": {
                    "width": "100%",
                    "margin": "0", 
                    "padding": "0",
                    "background-color": "#f8f9fa",
                    "height": "300px"
                },
                "title": {
                    "color": "#2e8b57"
                }
            }
        )
    
    with cols[1]:
        card(
            title="Call Us",
            text="(+91) 7265987469",
            image="https://images.unsplash.com/photo-1583394838336-acd977736f90?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=80",
            url="tel:+917265987469",
            styles={
                "card": {
                    "width": "100%",
                    "margin": "0", 
                    "padding": "0",
                    "background-color": "#f8f9fa",
                    "height": "300px"
                },
                "title": {
                    "color": "#2e8b57"
                }
            }
        )
    
    with cols[2]:
        card(
            title="Visit Us",
            text="Marwadi University, Morbi-Road Highway, Rajkot, Gujarat, India, 360003",
            image="https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=80",
            url="https://maps.app.goo.gl/Db1C3pVTmVVXA8nt5",
            styles={
                "card": {
                    "width": "100%",
                    "margin": "0", 
                    "padding": "0",
                    "background-color": "#f8f9fa",
                    "height": "300px"
                },
                "title": {
                    "color": "#2e8b57"
                }
            }
        )

    # ---- Contact Form ----
    st.markdown("---")
    st.subheader("📩 Send Us a Message")
    
    st.markdown("""
    <style>
        .contact-form {
            background-color: #f9f9f9;
            padding: 20px;
            border-radius: 12px;
            max-width: 500px;
            margin: auto;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .contact-form input, .contact-form textarea {
            width: 100%;
            padding: 10px;
            margin-top: 8px;
            margin-bottom: 16px;
            border: 1px solid #ccc;
            border-radius: 8px;
            box-sizing: border-box;
            font-size: 14px;
        }
        .contact-form button {
            background-color: #4CAF50;
            color: white;
            padding: 12px 20px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
        }
        .contact-form button:hover {
            background-color: #45a049;
        }
    </style>
    <div class="contact-form">
        <form action="https://formsubmit.co/c927f1508df2319903fe889d7857844a" method="POST">
            <label for="name">Your Name*</label>
            <input type="text" name="name" required placeholder="John Doe">
            <label for="email">Your Email*</label>
            <input type="email" name="email" required placeholder="you@example.com">
            <label for="message">Your Message*</label>
            <textarea name="message" rows="6" required placeholder="Write your message here..."></textarea>
            <!-- Hidden fields -->
            <input type="hidden" name="_captcha" value="false">
            <input type="hidden" name="_template" value="table">
            <input type="hidden" name="_subject" value="New Contact Form Submission">
            <input type="hidden" name="_autoresponse" value="Thanks for contacting us! We'll get back to you shortly.">
            <button type="submit">Send Message</button>
        </form>
    </div>
    """, unsafe_allow_html=True)
           
    # ---- Map Embed ----
    st.markdown("---")
    st.subheader("📍 Find Us on Map")
    st.components.v1.iframe(
        "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3690.0871183659556!2d70.80447287434623!3d22.350339141081683!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3959c82b45b79aef%3A0xaab1746ebf667e44!2s9R24%2B4RJ%20Marwadi%20University%2C%20Rajkot%20-%20Morbi%20Hwy%2C%20near%20Galaxy%20Prime%20Hostel%2C%20opposite%20APMC%20Yard%2C%20Bedi%2C%20Rajkot%2C%20Gujarat%20360003!5e0!3m2!1sen!2sin!4v1743506926729!5m2!1sen!2sin",
        height=400
    )

    # ---- Social Media ----
    st.markdown("---")
    st.subheader("💬 Connect With Us")
    
    social_cols = st.columns(4)
    with social_cols[0]:
        st.markdown("[![Twitter](https://img.icons8.com/color/48/000000/twitter--v1.png)](https://twitter.com)")
    with social_cols[1]:
        st.markdown("[![Instagram](https://img.icons8.com/color/48/000000/instagram-new.png)](https://www.instagram.com/hadush_negasii/profilecard/?igsh=MWYzanpmaGZnNGFkcA==)")
    with social_cols[2]:
        st.markdown("[![LinkedIn](https://img.icons8.com/color/48/000000/linkedin.png)](https://linkedin.com)")
    with social_cols[3]:
        st.markdown("[![Facebook](https://img.icons8.com/color/48/000000/facebook-new.png)](https://facebook.com)")
