FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy the entire project into the image
COPY . .

# Install Python dependencies from the scraper API requirements
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8000

# Command to run the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
