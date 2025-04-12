import streamlit as st

def footer():
    st.markdown("---")
    st.components.v1.html(
        """
        <style>
        .simple-footer {
            background: #111827;
            color: #ffffff;
            padding: 2rem 1rem;
            text-align: center;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .footer-content {
            max-width: 600px;
            margin: 0 auto;
        }
        .footer-logo {
            font-size: 1.6rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            color: #ffffff;
        }
        .footer-tagline {
            color: #9CA3AF;
            line-height: 1.5;
            margin-bottom: 1.2rem;
            font-size: 0.95rem;
        }
        .social-links {
            display: flex;
            justify-content: center;
            gap: 1.2rem;
            margin-bottom: 1.5rem;
        }
        .social-links a {
            color: #ffffff;
            font-size: 1.2rem;
            transition: transform 0.2s ease;
        }
        .social-links a:hover {
            transform: translateY(-2px);
            opacity: 0.8;
        }
        .footer-copyright {
            color: #6B7280;
            font-size: 0.85rem;
            padding-top: 1.2rem;
            border-top: 1px solid rgba(255,255,255,0.1);
        }
        </style>

        <div class="simple-footer">
            <div class="footer-content">
                <div class="footer-logo">RecipeFinder</div>
                <p class="footer-tagline">
                    Personalized recipe recommendations using machine learning
                </p>
                <div class="social-links">
                    <a href="https://github.com/hadush-negasi" aria-label="GitHub" target="_blank" rel="noopener noreferrer">
                        <i class="fab fa-github"></i>
                    </a>
                    <a href="mailto:hadush7512@gmail.com" aria-label="Email" target="_blank" rel="noopener noreferrer">
                        <i class="fas fa-envelope"></i>
                    </a>

                    <a href="https://www.instagram.com/hadush_negasii/profilecard/?igsh=MWYzanpmaGZnNGFkcA==" aria-label="Instagram" target="_blank" rel="noopener noreferrer">
                        <i class="fab fa-instagram"></i>
                    </a>

                    <a href="https://www.linkedin.com/in/hadush-brhane" aria-label="Linkedin" target="_blank" rel="noopener noreferrer">
                        <i class="fab fa-linkedin"></i>
                    </a>

                </div>
                <div class="footer-copyright">
                    © 2025 RecipeFinder | By Hadush Negasi
                </div>
            </div>
        </div>

        <!-- Font Awesome for icons -->
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        """,
        height=250,
    )   