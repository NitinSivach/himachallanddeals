import streamlit as st
from streamlit_option_menu import option_menu
from PIL import Image
import base64
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import re

# Initialize session state for form
if 'form_submitted' not in st.session_state:
    st.session_state.form_submitted = False
if 'enquiry_property' not in st.session_state:
    st.session_state.enquiry_property = None

# Load configuration from Streamlit secrets or .env file
def get_config(key, default=None):
    """Get configuration from Streamlit secrets or .env file"""
    try:
        # First try to get from Streamlit secrets (for production)
        if key in st.secrets:
            return st.secrets[key]
        # Fall back to .env file (for local development)
        load_dotenv()
        return os.getenv(key, default)
    except Exception as e:
        # If secrets aren't available, fall back to environment variables
        load_dotenv()
        return os.getenv(key, default)

def send_email(name, email, phone, message, property_name=None):
    """Send an email with the enquiry details using Gmail SMTP"""
    try:
        # Email configuration
        sender_email = get_config('EMAIL_HOST_USER')
        receiver_email = get_config('RECIPIENT_EMAIL')
        password = get_config('EMAIL_HOST_PASSWORD', '').strip('"\'')
        
        if not all([sender_email, receiver_email, password]):
            st.error("Email configuration is incomplete. Please check your settings.")
            return False
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = f"New Property Enquiry - {property_name if property_name else 'General'}"
        
        # Email body
        body = f"""
        <h2>New Property Enquiry</h2>
        <p><strong>Property:</strong> {property_name if property_name else 'General Enquiry'}</p>
        <p><strong>Name:</strong> {name}</p>
        <p><strong>Email:</strong> {email}</p>
        <p><strong>Phone:</strong> {phone}</p>
        <p><strong>Message:</strong></p>
        <p>{message}</p>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # Send email with better error handling
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            
            try:
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email, msg.as_string())
                return True
            except smtplib.SMTPAuthenticationError as e:
                st.error("Authentication failed. Please check your email and App Password.")
                st.error(f"Error details: {str(e)}")
                return False
            except Exception as e:
                st.error(f"Error sending email: {str(e)}")
                return False
                
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
        return False

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validate Indian phone number"""
    pattern = r'^[6-9]\d{9}$'
    return re.match(pattern, phone) is not None

# Page configuration
st.set_page_config(
    page_title="Himachal Land Deals",
    page_icon="🏞️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
def load_css():
    st.markdown("""
    <style>
        /* Main container */
        .main {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 1rem;
        }
        
        /* Header */
        .header {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 2rem 0;
            text-align: center;
            border-radius: 10px;
            margin-bottom: 2rem;
        }
        
        /* Property cards */
        .property-card {
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s;
            margin-bottom: 2rem;
            background: white;
        }
        
        .property-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }
        
        /* Contact form */
        .contact-form {
            background: #f8f9fa;
            padding: 2rem;
            border-radius: 10px;
            margin-top: 2rem;
        }
        
        /* Footer */
        .footer {
            background: #2c3e50;
            color: white;
            padding: 2rem 0;
            margin-top: 3rem;
            text-align: center;
        }
        
        /* Responsive design */
        @media (max-width: 768px) {
            .property-card {
                margin-bottom: 1.5rem;
            }
        }
    </style>
    """, unsafe_allow_html=True)

def main():
    # Load CSS
    load_css()
    
    # Initialize session state for navigation
    if 'selected_tab' not in st.session_state:
        st.session_state.selected_tab = "Home"
    
    # Update selected tab from URL if present
    if 'tab' in st.query_params:
        st.session_state.selected_tab = st.query_params['tab']
    
    # Get contact info at the start of main
    office_address = get_config('OFFICE_ADDRESS', 'Solan, By pass road, Near New Bus Stand, Himachal Pradesh')
    contact_phone = get_config('CONTACT_PHONE', '+91 XXXXXXXXXX')
    contact_email = get_config('CONTACT_EMAIL', 'contact@example.com')
    website_url = get_config('WEBSITE_URL', 'sivachnitinkumar@gmail.com')
    
    # Initialize session state
    if 'form_submitted' not in st.session_state:
        st.session_state.form_submitted = False
    if 'enquiry_property' not in st.session_state:
        st.session_state.enquiry_property = None
    if 'contact_expanded' not in st.session_state:
        st.session_state.contact_expanded = False
    
    # Handle URL parameters
    if 'enquire' in st.query_params and st.query_params['enquire'] == 'true':
        st.session_state.contact_expanded = True
        st.session_state.form_submitted = False
        if 'property' in st.query_params:
            st.session_state.enquiry_property = st.query_params['property']
    
    # Navigation
    with st.container():
        # Create a callback to update the URL when a tab is selected
        def on_tab_change(*args):
            st.query_params.clear()
            st.query_params['tab'] = st.session_state.nav_menu
            st.session_state.selected_tab = st.session_state.nav_menu
        
        # Get the selected tab from session state
        selected = st.session_state.selected_tab
        
        # Create the navigation menu
        selected = option_menu(
            menu_title=None,
            options=["Home", "Properties", "About", "Contact"],
            icons=["house", "map", "info-circle", "envelope"],
            menu_icon="cast",
            default_index=["Home", "Properties", "About", "Contact"].index(selected) if selected in ["Home", "Properties", "About", "Contact"] else 0,
            orientation="horizontal",
            styles={
                "container": {"padding": "0!important", "background-color": "#f8f9fa"},
                "nav-link": {"font-size": "16px", "text-align": "center", "margin":"0px", "--hover-color": "#eee"},
                "nav-link-selected": {"background-color": "#1e3c72"},
            },
            key="nav_menu",
            on_change=on_tab_change
        )
        
        # Override selection if coming from enquiry
        if st.session_state.contact_expanded:
            selected = "Contact"
            st.session_state.selected_tab = "Contact"
            st.query_params.clear()
            st.query_params['tab'] = "Contact"
    
    # Home Section
    if selected == "Home":
        st.markdown("""
        <div class="header">
            <h1>Himachal Land Deals</h1>
            <p>Your Trusted Partner for Premium Land Deals in Himachal Pradesh</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        ## Welcome to Himachal Land Deals
        
        Discover the most beautiful and valuable land properties in the serene landscapes of Himachal Pradesh. 
        Whether you're looking for a peaceful retreat, an investment opportunity, or your dream home location, 
        we have the perfect piece of land for you.
        """)
        
        # Featured Properties
        st.header("✨ Featured Properties")
        col1, col2 = st.columns(2)
        
        with col1:
            with st.container():
                st.markdown("""
                <div class="property-card">
                    <img src="https://images.unsplash.com/photo-1600585154340-be6161a56a0c?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80" 
                         style="width:100%; height:200px; object-fit: cover;">
                    <div style="padding: 1rem;">
                        <h3>Mountain View Plots</h3>
                        <p>📍 Shimla, Himachal Pradesh</p>
                        <p>Starting from ₹25 Lakhs</p>
                        <p>Panoramic mountain views, gated community, 24/7 security</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            with st.container():
                st.markdown("""
                <div class="property-card">
                    <img src="https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80" 
                         style="width:100%; height:200px; object-fit: cover;">
                    <div style="padding: 1rem;">
                        <h3>Riverside Land Parcels</h3>
                        <p>📍 Kullu, Himachal Pradesh</p>
                        <p>Starting from ₹35 Lakhs</p>
                        <p>Adjacent to river, lush green surroundings, peaceful environment</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # Properties Section
    elif selected == "Properties":
        st.header("🏞️ Available Properties")
        
        # Property 1
        with st.expander("🌄 Premium Hilltop Land - Shimla", expanded=True):
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image("https://images.unsplash.com/photo-1580587771525-78b9dba3b914?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80", 
                        use_container_width=True)
            with col2:
                st.subheader("Premium Hilltop Land")
                st.markdown("""
                - 📍 Location: Shimla, Himachal Pradesh
                - 📏 Area: 5-10 Acres available
                - 💰 Price: ₹30 Lakhs - ₹50 Lakhs per acre
                - 🌟 Features: 
                    - Breathtaking valley views
                    - All-weather road connectivity
                    - Clear titles with proper documentation
                    - Ideal for resort or farmhouse
                """)
                if st.button("Enquire Now", key="property1"):
                    st.session_state.contact_expanded = True
                    st.session_state.enquiry_property = "Premium Hilltop Land - Shimla"
                    st.session_state.form_submitted = False
                    st.query_params.clear()
                    st.query_params['enquire'] = 'true'
                    st.query_params['property'] = "Premium Hilltop Land - Shimla"
                    st.query_params['tab'] = 'Contact'
                    st.rerun()
        
        # Property 2
        with st.expander("🌲 Forest Facing Plots - Manali", expanded=True):
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image("https://images.unsplash.com/photo-1600566752225-7a0c8b5c1b5f?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80", 
                        use_container_width=True)
            with col2:
                st.subheader("Forest Facing Plots")
                st.markdown("""
                - 📍 Location: Manali, Himachal Pradesh
                - 📏 Area: 2400-5000 sq.ft. plots
                - 💰 Price: ₹2000-₹2500 per sq.ft.
                - 🌟 Features: 
                    - Dense deodar forest view
                    - Gated community
                    - Water and electricity connections
                    - 10 minutes from Manali Mall Road
                """)
                if st.button("Enquire Now", key="property2"):
                    st.session_state.contact_expanded = True
                    st.session_state.enquiry_property = "Forest Facing Plots - Manali"
                    st.session_state.form_submitted = False
                    st.query_params.clear()
                    st.query_params['enquire'] = 'true'
                    st.query_params['property'] = "Forest Facing Plots - Manali"
                    st.query_params['tab'] = 'Contact'
                    st.rerun()
    
    # About Section
    elif selected == "About":
        st.header("🏔️ About Us")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.image("https://images.unsplash.com/photo-1501785888041-af3ef285b470?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80", 
                    use_container_width=True)
        
        with col2:
            st.markdown("""
            ## Our Story
            
            Established in 2010, Himachal Land Deals has been a trusted name in the real estate sector of Himachal Pradesh. 
            With over a decade of experience, we have helped hundreds of clients find their dream properties in the lap of the Himalayas.
            
            ### Why Choose Us?
            - 🏆 12+ Years of Experience
            - 📜 Verified and Clear Titles
            - 🏡 500+ Happy Clients
            - 🏢 50+ Successful Projects
            - 🤝 Transparent Deals
            
            Our team of local experts has in-depth knowledge of the region's real estate market, ensuring you get the best deals 
            with complete transparency and legal compliance.
            """)
    
    # Contact Section
    elif selected == "Contact" or st.session_state.get('contact_expanded', False) or st.session_state.get('form_submitted', False):
        # Reset the contact_expanded flag after loading the contact section
        st.session_state.contact_expanded = False
        
        if st.session_state.get('form_submitted', False):
            # Show thank you message
            st.balloons()
            st.header("🎉 Thank You!")
            st.markdown("""
            <div style='text-align: center; padding: 2rem; background-color: #f0f2f6; border-radius: 10px; margin: 2rem 0;'>
                <h2>Your Enquiry Has Been Received!</h2>
                <p>We've received your enquiry about <strong>{}</strong>.</p>
                <p>Our team will contact you shortly at the provided contact details.</p>
                <p style='margin-top: 2rem;'>
                    <a href='/?nav=Home' class='stButton'>
                        <button style='background-color: #1e3c72; color: white; border: none; padding: 0.5rem 1rem; border-radius: 5px; cursor: pointer;'>
                            Back to Home
                        </button>
                    </a>
                </p>
            </div>
            """.format(st.session_state.enquiry_property or 'our properties'), unsafe_allow_html=True)
            
            # Reset form state after showing thank you
            if st.button("Submit Another Enquiry"):
                st.session_state.form_submitted = False
                st.session_state.enquiry_property = None
                st.rerun()
                
        else:
            st.header("📞 Contact Us")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Get in Touch")
                st.markdown(f"""
                ### Office Address
                📍 {office_address}
                
                ### Contact Information
                📞 {contact_phone}
                📧 {contact_email}
                🌐 {website_url}
                
                ### Office Hours
                🕘 Monday - Saturday: 9:00 AM - 6:00 PM  
                🚪 Sunday: Closed
                """)
                
                # Social Media Links
                st.markdown("### Follow Us")
                st.markdown("""
                [![Facebook](https://img.icons8.com/color/48/000000/facebook-new.png)](https://facebook.com)
                [![Instagram](https://img.icons8.com/color/48/000000/instagram-new.png)](https://instagram.com)
                [![Twitter](https://img.icons8.com/color/48/000000/twitter.png)](https://twitter.com)
                [![LinkedIn](https://img.icons8.com/color/48/000000/linkedin.png)](https://linkedin.com)
                """, unsafe_allow_html=True)
            
            with col2:
                with st.form("contact_form"):
                    st.subheader("Send us a Message")
                    
                    # Pre-fill property name if coming from an enquiry
                    property_name = st.session_state.enquiry_property or ""
                    if property_name:
                        st.info(f"Enquiring about: {property_name}")
                    
                    name = st.text_input("Your Name*")
                    email = st.text_input("Email Address*")
                    phone = st.text_input("Phone Number*")
                    subject = st.selectbox("Subject", 
                                        ["General Inquiry", "Property Inquiry", "Appointment Request", "Other"])
                    message = st.text_area("Your Message*", height=150, 
                                         value=f"I'm interested in {property_name}. " if property_name else "")
                    
                    # Form submission
                    submitted = st.form_submit_button("Send Message")
                    if submitted:
                        if not all([name, email, phone, message]):
                            st.error("Please fill in all required fields.")
                        elif not validate_email(email):
                            st.error("Please enter a valid email address.")
                        elif not validate_phone(phone):
                            st.error("Please enter a valid 10-digit Indian phone number.")
                        else:
                            # Send email
                            email_sent = send_email(
                                name=name,
                                email=email,
                                phone=phone,
                                message=message,
                                property_name=property_name or "General Enquiry"
                            )
                            
                            if email_sent:
                                st.session_state.form_submitted = True
                                st.session_state.enquiry_property = property_name
                                st.rerun()
                            else:
                                st.error("Failed to send your message. Please try again later or contact us directly.")
    
    # Get contact info
    office_address = get_config('OFFICE_ADDRESS', 'Solan, By pass road, Near New Bus Stand, Himachal Pradesh')
    contact_phone = get_config('CONTACT_PHONE', '+91 XXXXXXXXXX')
    contact_email = get_config('CONTACT_EMAIL', 'contact@example.com')
    website_url = get_config('WEBSITE_URL', 'www.himachallanddeals.com')
    
    # Footer
    st.markdown(f"""
    <div class="footer">
        <p>© 2025 Himachal Land Deals. All Rights Reserved.</p>
        <p>📍 {office_address}</p>
        <p>📞 {contact_phone} | ✉️ {contact_email} | 🌐 {website_url}</p>
        <p>Designed with ❤️ by Himachal Land Deals</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
