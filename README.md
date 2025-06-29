# Bike Inventory Web App

A web app to manage your bike parts inventory, with barcode scanning and HTTPS support for iOS/desktop Safari.

## Features
- Add/search/edit/delete bike parts (title, GTIN, image, category)
- Barcode scanner for adding/searching items (camera access)
- Responsive UI for iPhone and desktop
- Secure local HTTPS access via Docker Compose

## Getting Started
1. Clone the repo
2. Run `docker-compose up --build`
3. Access the app at https://localhost

## Tech Stack
- React (frontend)
- Node.js/Express (backend)
- SQLite (database)
- Docker Compose (deployment)
