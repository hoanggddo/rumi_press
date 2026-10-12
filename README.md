#  Rumi Press Book Distribution Management System

A full-stack Django web application designed to replace spreadsheet-based workflows for managing book distribution operations.

##  Overview

This project simulates a real-world business scenario where a publishing/distribution company transitions from manual spreadsheet tracking to a centralized, web-based system.

The application enables efficient management of books, categories, and distribution expenses, while providing search functionality and visual insights through reporting dashboards.

---

##  Features

- User authentication using Django's built-in auth system  
-  Manage books (title, author, category, expenses)  
-  Create and manage book categories  
-  Search functionality for quick data retrieval  
- Expense reporting with category-based visualizations  
-  Full CRUD operations with validation and error handling  
-  Migration of legacy spreadsheet data into the system  
-  Deployed and accessible online  

---

##  Tech Stack

- **Backend:** Python, Django  
- **Frontend:** HTML, Bootstrap  
- **Database:** SQLite (development)  
- **Version Control:** Git / GitHub  
- **Deployment:** Render  

---

##  Key Functionality

- Designed relational data models using Django ORM  
- Implemented secure authentication and session handling  
- Built dynamic views and templates for data interaction  
- Developed reporting dashboards to analyze expense distribution  
- Ensured data integrity with validation and error handling  

---

##  Live Demo

👉 https://rumi-press-22f5.onrender.com

---

## Password Reset Email

The app uses Resend's HTTPS API when `RESEND_API_KEY` is configured. This is the recommended option for Render's free web services, which block outbound SMTP ports. To enable password reset email:

1. Verify a sending domain in Resend and create an API key.
2. Add these environment variables in Render (or to your local, Git-ignored `.env` file):

```text
RESEND_API_KEY=re_your_resend_api_key
DEFAULT_FROM_EMAIL=Rumi Press <no-reply@your-verified-domain.com>
```

Replace the example API key and sender address with your own values. The sender address must use the domain you verified in Resend. Keep the API key in environment settings; do not commit it to the repository.

3. Redeploy the app, request a password reset for an account whose email you can access, and confirm the message arrives and the reset link works. The API connection has a short timeout so a stalled provider request won't leave the page waiting indefinitely.

Without `RESEND_API_KEY` or `EMAIL_HOST`, Django uses its console email backend. Reset requests won't send a real email; the message is written to the application logs instead.

##  What I Learned

- Building full-stack applications with Django  
- Structuring and querying relational databases  
- Implementing authentication and user management  
- Translating business requirements into technical solutions  
- Deploying and maintaining a live web application  

---

##  Future Improvements

- Add REST API using Django REST Framework  
- Implement pagination for large datasets  
- Enhance UI/UX design  
- Upgrade to PostgreSQL for production  
- Add role-based access control  


---

##  Contributing

This is a personal project, but feedback and suggestions are welcome!

---

##  License

This project is for educational and portfolio purposes.
