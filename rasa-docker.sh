#!/bin/bash

# Helper script for managing Rasa in Docker

function show_help {
  echo "Rasa Docker Helper Script"
  echo ""
  echo "Usage: $0 [command]"
  echo ""
  echo "Commands:"
  echo "  start         - Start the Rasa server"
  echo "  stop          - Stop the Rasa server"
  echo "  train         - Train a new model"
  echo "  shell         - Open a shell in the Rasa container"
  echo "  logs          - View logs from the Rasa container"
  echo "  status        - Check status of the Rasa container"
  echo "  test          - Run tests"
  echo "  rebuild       - Rebuild the Docker image"
  echo "  restart       - Restart the Rasa server"
  echo "  help          - Show this help message"
}

# Check if a command was provided
if [ $# -eq 0 ]; then
    show_help
    exit 1
fi

# Process commands
case "$1" in
    start)
        echo "Starting Rasa server..."
        docker-compose up -d
        echo "Rasa server started at http://localhost:5005/"
        ;;
    stop)
        echo "Stopping Rasa server..."
        docker-compose down
        echo "Rasa server stopped"
        ;;
    train)
        echo "Training Rasa model..."
        docker exec -it rasa_project-rasa-1 rasa train
        echo "Training completed"
        ;;
    shell)
        echo "Opening shell in Rasa container..."
        docker exec -it rasa_project-rasa-1 bash
        ;;
    logs)
        echo "Showing logs from Rasa container..."
        docker logs -f rasa_project-rasa-1
        ;;
    status)
        echo "Checking status of Rasa container..."
        docker-compose ps
        ;;
    test)
        echo "Running tests..."
        docker exec -it rasa_project-rasa-1 rasa test
        echo "Tests completed"
        ;;
    rebuild)
        echo "Rebuilding Docker image..."
        docker-compose build
        echo "Rebuild completed"
        ;;
    restart)
        echo "Restarting Rasa server..."
        docker-compose down
        docker-compose up -d
        echo "Rasa server restarted at http://localhost:5005/"
        ;;
    help)
        show_help
        ;;
    *)
        echo "Unknown command: $1"
        show_help
        exit 1
        ;;
esac

exit 0 