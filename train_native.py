#!/usr/bin/env python
"""
Native Rasa training script for M1/M2 Macs
"""
import os
import sys
import subprocess
import tempfile
import shutil
import time

def check_requirements():
    """Check if required packages are installed."""
    try:
        import tensorflow
        import numpy
        print(f"TensorFlow version: {tensorflow.__version__}")
        print(f"NumPy version: {numpy.__version__}")
        return True
    except ImportError:
        print("Error: Required packages not installed.")
        print("Please install the required packages with:")
        print("pip install 'tensorflow>=2.10.0' numpy==1.24.3")
        return False

def train_model():
    """Train the Rasa model natively."""
    start_time = time.time()
    print("Training Rasa model natively on M1/M2 Mac...")
    
    # Set environment variables for better performance
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"  # Reduce TensorFlow noise
    os.environ["OMP_NUM_THREADS"] = "4"       # Control number of threads
    
    # Run Rasa training with simplified configuration
    cmd = [
        "python", "-m", "rasa", "train",
        "--config", "config.yml",
        "--num-threads", "4",
        "--augmentation", "0"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        duration = time.time() - start_time
        print(f"Training completed in {duration:.2f} seconds")
        
        # List trained models
        print("\nAvailable models:")
        for model in os.listdir("models"):
            if model.endswith(".tar.gz"):
                print(f"- models/{model}")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error during training: {e}")
        return False

def install_requirements():
    """Install required packages for native training."""
    print("Installing required packages...")
    
    # Use separate installation steps for better compatibility
    try:
        # First install TensorFlow
        subprocess.run([sys.executable, "-m", "pip", "install", "tensorflow>=2.10.0"], check=True)
        print("TensorFlow installed successfully")
        
        # Then install Rasa and other dependencies
        packages = [
            "numpy==1.24.3",
            "rasa==3.5.14",
            "sqlalchemy<2.0"
        ]
        subprocess.run([sys.executable, "-m", "pip", "install"] + packages, check=True)
        print("Rasa and other packages installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing packages: {e}")
        return False

def main():
    """Main function."""
    print("Rasa Native Training for M1/M2 Mac")
    print("=================================")
    
    if not check_requirements():
        choice = input("Would you like to install the required packages? (y/n): ")
        if choice.lower() == 'y':
            if not install_requirements():
                return
        else:
            print("Exiting. Please install the required packages manually.")
            return
    
    print("\nStarting model training...")
    train_model()
    
    print("\nTo use the trained model with Docker, copy the model file to the Docker container:")
    print("docker cp models/<model_file.tar.gz> rasa_project-rasa-1:/app/models/")
    print("docker-compose restart rasa")

if __name__ == "__main__":
    main() 