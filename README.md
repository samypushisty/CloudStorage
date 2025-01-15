# Cloud Storage Application

## Overview

This application serves as a cloud storage solution developed for educational purposes. The primary objective of this project is to explore and master new technologies before integrating them into our main project.

## Features

- **File Upload with Delayed Deletion**: Users can upload files and specify a deletion time in minutes. The deletion is managed through a queue of delayed tasks using Celery.
- **File Download**: Users can easily download their uploaded files.
- **File Deletion**: Users have the option to delete files manually.
- **Unique Access via IDs**: Each file is associated with a unique ID assigned to the file, ensuring secure and individual access.
- **Task Management with Celery**: Background tasks for file deletion are handled by Celery workers.
- **Redis for Task Storage**: Tasks are stored in Redis for convenience and efficiency, with Redis deployed using Docker Compose.
- **FastAPI Backend**: The backend is developed using FastAPI.

## Technologies Used

- **Backend**: FastAPI
- **Database**: Redis (for task management)
- **Task Queue**: Celery
- **Containerization**: Docker Compose

## Installation
