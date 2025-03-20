# use python 3.10 as the base image  
FROM python:3.10  

# set the working directory inside the container  
WORKDIR /app  

# copy all files from your repo to the container  
COPY . .  

# install dependencies  
RUN pip install --no-cache-dir -r requirements.txt  

# expose port 8000  
EXPOSE 8000  

# command to run the app  
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
