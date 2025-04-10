#!/bin/bash

# Script to run the Tweet Extractor application and tests

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to print section header
print_header() {
    echo -e "\n${YELLOW}=== $1 ===${NC}\n"
}

# Check if Python is installed
if ! command_exists python3; then
    echo -e "${RED}Error: Python 3 is not installed.${NC}"
    exit 1
fi

# Check if Chrome is installed
if ! command_exists google-chrome || ! command_exists google-chrome-stable; then
    echo -e "${YELLOW}Warning: Chrome does not appear to be installed. Selenium may not work correctly.${NC}"
fi

# Parse command line arguments
case "$1" in
    "server")
        print_header "Starting Tweet Extractor Server"
        python3 railway_app.py
        ;;
    "test")
        print_header "Running Tweet Extractor Test"
        python3 test_selenium_extractor.py
        ;;
    "docker")
        if ! command_exists docker; then
            echo -e "${RED}Error: Docker is not installed.${NC}"
            exit 1
        fi
        print_header "Building and Running with Docker"
        docker build -t tweet-extractor .
        docker run -p 8080:8080 tweet-extractor
        ;;
    "docker-compose")
        if ! command_exists docker-compose; then
            echo -e "${RED}Error: Docker Compose is not installed.${NC}"
            exit 1
        fi
        print_header "Running with Docker Compose"
        docker-compose up
        ;;
    "install")
        print_header "Installing Dependencies"
        pip install -r requirements.txt
        echo -e "${GREEN}Dependencies installed successfully.${NC}"
        ;;
    *)
        echo -e "${YELLOW}Tweet Extractor Runner${NC}"
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  server         Start the Flask server"
        echo "  test           Run the test script"
        echo "  docker         Build and run with Docker"
        echo "  docker-compose Run with Docker Compose"
        echo "  install        Install Python dependencies"
        ;;
esac
