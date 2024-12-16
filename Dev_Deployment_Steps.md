
# README: Deploying Django Rest Framework (DRF) in a Development Environment

This guide provides step-by-step instructions for deploying a Django Rest Framework (DRF) application on a virtual machine (VM) for a development environment.

## Prerequisites

- A virtual machine (VM) with SSH access.
- Python 3.12 installed on the VM.
- GitHub repository access (SSH key configured).
- Basic knowledge of the command line.

## Steps to Deploy the DRF Application

### 1. Create SSH Keys (if not already done)

If you haven't already created SSH keys on your VM, follow these steps:

#### Generate SSH keys
```
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
```

#### Start the SSH agent
```
eval "$(ssh-agent -s)"
```

#### Add the SSH key to the agent
```
ssh-add ~/.ssh/id_rsa
```

#### Display the public key
```
cat ~/.ssh/id_rsa.pub
```

Copy the public key and add it to your GitHub account under Settings > SSH and GPG keys.

### 2. Verify Python Version

Ensure that Python 3.12 is installed on your VM:
```
python3 --version
```

If Python 3.12 is not installed, install it using your package manager or download it from the official Python website.

### 3. Clone the GitHub Repository

Clone the develop branch of the repository:
```
git clone --branch develop --single-branch git@github.com:AlgorithmxTech/DIY-Internal-Backend.git
```

#### Navigate into the project directory
```
cd DIY-Internal-Backend
```

### 4. Create a .env File

Please see the env.sample to know what variables need to be added. Check vaultwarden for the actual keys required for the development environment.

Create a .env file in the project root directory to store environment-specific variables:
```
touch .env
```

Add the necessary environment variables to the .env file. For example:
```
DEBUG=True
SECRET_KEY=your_secret_key
DATABASE_URL=postgres://user:password@localhost:5432/dbname
```

### 5. Create a Virtual Environment

Create a virtual environment to isolate project dependencies:
```
python3 -m venv venv
```

### 6. Activate the Virtual Environment

Activate the virtual environment:

#### On macOS/Linux
```
source venv/bin/activate
```

#### On Windows
```
venv\Scripts\activate
```

### 7. Install Dependencies

Install the required Python packages using pip:
```
pip install -r requirements.txt
```

### 8. Configure CORS for Development, if you want to connect the react frontend via localhost

To enable Cross-Origin Resource Sharing (CORS) for development:

#### Install `django-cors-headers`
```
pip install django-cors-headers
```

#### Update Django settings
Add the following configuration to your `settings.py` file:
```python
INSTALLED_APPS += ['corsheaders']

MIDDLEWARE.insert(0, 'corsheaders.middleware.CorsMiddleware')

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

CORS_ORIGIN_WHITELIST = [
    'http://10.0.0.8:5173',
    'http://localhost:5173',  # React development server
    'http://127.0.0.1:5173',  # React development server
    'http://192.168.8.149:8000',
    'http://0.0.0.0:5173',
]
```

### 9. Run the Django Development Server

Navigate to the project directory and start the development server:

```
cd project_name  # Replace with the actual project directory name
```

#### Run the development server
```
python3 manage.py runserver 0.0.0.0:8000
```

## Access the Application

Once the server is running, you can access the application by navigating to:
```
http://<VM_IP_ADDRESS>:8000
```

Replace `<VM_IP_ADDRESS>` with the IP address of your VM.

## Notes

- Ensure that the VM's firewall allows incoming traffic on port 8000.
- For production environments, consider using a production-ready server like Gunicorn or uWSGI, and configure a reverse proxy (e.g., Nginx or Apache).

## Troubleshooting

- If you encounter issues with SSH key authentication, verify that the SSH key is correctly added to GitHub and the SSH agent.
- If dependencies fail to install, ensure that the requirements.txt file is up-to-date and compatible with Python 3.12.

This setup is intended for development purposes. For production, additional configurations such as HTTPS, environment variable management, and database setup are required.
