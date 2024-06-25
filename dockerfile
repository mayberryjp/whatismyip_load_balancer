# Use an official Python runtime as the base image
ARG CACHEBUST=1 
FROM python:3.11.7

# Set the working directory
WORKDIR /whatismyip_load_balancer-v1.0.26

# Copy the requirements file
#COPY requirements.txt .
#RUN cd /
RUN git clone https://github.com/mayberryjp/whatismyip_load_balancer.git .
# Create a virtual environment and install the dependencies
RUN python -m venv venv
RUN venv/bin/pip install --upgrade pip
RUN venv/bin/pip install paho.mqtt
RUN venv/bin/pip install requests


# Copy the app files
#COPY myapp/ .

# Expose the port
#EXPOSE 5102

# Run the app
CMD ["venv/bin/python","-u", "whatismyip_load_balancer.py"]