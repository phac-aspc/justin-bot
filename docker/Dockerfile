# Set base image (host OS)
FROM python:3.11-slim

# By default, listen on port 5555
EXPOSE 5555

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY ../requirements.txt ./

# Install any dependencies
RUN pip install -r requirements.txt

# Copy backend files necessary for the API
COPY ../api.py ./
COPY ../backend.py ./
COPY ../.env ./
COPY ../processed/ ./processed/

# Specify the command to run on container start
CMD [ "python", "./api.py" ]