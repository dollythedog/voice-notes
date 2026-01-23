#!/bin/bash
# Helper script for managing the voice transcription service

case "$1" in
    start)
        echo "Starting voice transcription service..."
        sudo systemctl start voice-transcription.service
        ;;
    stop)
        echo "Stopping voice transcription service..."
        sudo systemctl stop voice-transcription.service
        ;;
    restart)
        echo "Restarting voice transcription service..."
        sudo systemctl restart voice-transcription.service
        ;;
    status)
        sudo systemctl status voice-transcription.service --no-pager
        ;;
    logs)
        echo "Recent logs (Ctrl+C to exit):"
        sudo journalctl -u voice-transcription.service -f
        ;;
    logs-recent)
        echo "Last 50 log lines:"
        sudo journalctl -u voice-transcription.service -n 50 --no-pager
        ;;
    test)
        echo "Testing with a file in inbox..."
        if [ -z "$2" ]; then
            echo "Usage: $0 test <audio_file>"
            echo "Example: $0 test sample.m4a"
            exit 1
        fi
        if [ ! -f "$2" ]; then
            echo "Error: File $2 not found"
            exit 1
        fi
        echo "Copying $2 to inbox..."
        cp "$2" /srv/voice_notes/inbox/
        echo "File copied. Watch logs with: $0 logs"
        ;;
    *)
        echo "Voice Transcription Service Control"
        echo ""
        echo "Usage: $0 {start|stop|restart|status|logs|logs-recent|test <file>}"
        echo ""
        echo "Commands:"
        echo "  start       - Start the service"
        echo "  stop        - Stop the service"
        echo "  restart     - Restart the service"
        echo "  status      - Show service status"
        echo "  logs        - Follow live logs (Ctrl+C to exit)"
        echo "  logs-recent - Show last 50 log lines"
        echo "  test <file> - Test with an audio file"
        echo ""
        exit 1
        ;;
esac
