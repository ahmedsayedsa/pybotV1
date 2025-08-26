# WhatsApp Subscription Management System

A FastAPI-based system for managing WhatsApp subscriptions with user and admin roles.

## Features

- User registration and authentication (JWT)
- Admin panel for user management
- Subscription expiry management
- Role-based access control
- Firebase Firestore integration

## Setup

1. Clone the repository
2. Copy `.env.example` to `.env` and configure your Firebase credentials
3. Install dependencies: `pip install -r requirements.txt`
4. Run the application: `uvicorn src.app:app --reload`

## Docker

```bash
docker build -t whatsapp-subscription .
docker run -p 8080:8080 --env-file .env whatsapp-subscription