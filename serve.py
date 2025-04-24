import http.server
import socketserver
import os
import re
import socket
import sys

def find_available_port(start_port=5500, max_attempts=10):
    """Find an available port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(('', port))
            s.close()
            return port
        except OSError:
            continue
    raise RuntimeError(f"Could not find an available port after {max_attempts} attempts")

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Ensure the outputs directory exists
        if not os.path.exists('outputs'):
            os.makedirs('outputs')
        
        # Convert to absolute path to handle Windows paths better
        directory = os.path.abspath('outputs')
        super().__init__(*args, directory=directory, **kwargs)

    def do_GET(self):
        try:
            # Get the requested file path
            path = self.translate_path(self.path)
            
            # Check if the file exists
            if os.path.isfile(path):
                # Read the file content
                with open(path, 'rb') as file:
                    content = file.read()
                
                # If it's an HTML file, modify the content to use absolute paths
                if path.endswith('.html'):
                    try:
                        content = content.decode('utf-8')
                        # Replace relative paths with absolute paths for Plotly resources
                        content = re.sub(
                            r'(src|href)="(plotly|require)',
                            r'\1="https://cdn.plot.ly/\2',
                            content
                        )
                        content = content.encode('utf-8')
                    except Exception as e:
                        print(f"Error processing HTML file: {e}")
                        self.send_error(500, f"Error processing HTML file: {str(e)}")
                        return
                
                # Send the response
                self.send_response(200)
                self.send_header('Content-type', self.guess_type(path))
                self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                self.send_header('Pragma', 'no-cache')
                self.send_header('Expires', '0')
                self.end_headers()
                self.wfile.write(content)
            else:
                available_files = [f for f in os.listdir(self.directory) if f.endswith('.html')]
                error_message = f"File not found. Available files: {', '.join(available_files)}"
                self.send_error(404, error_message)
        except Exception as e:
            print(f"Error serving request: {e}")
            self.send_error(500, f"Internal server error: {str(e)}")

def main():
    try:
        # Find an available port
        port = find_available_port()
        
        # Create server
        handler = Handler
        with socketserver.TCPServer(("", port), handler) as httpd:
            print(f"\nServer started successfully!")
            print(f"Serving files from: {os.path.abspath('outputs')}")
            print(f"Server URL: http://127.0.0.1:{port}")
            print(f"\nAvailable files:")
            
            # List available files
            for file in os.listdir('outputs'):
                if file.endswith('.html'):
                    print(f"  - http://127.0.0.1:{port}/{file}")
            
            print("\nPress Ctrl+C to stop the server")
            
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\nServer stopped by user")
                sys.exit(0)
    
    except Exception as e:
        print(f"\nError starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 