FROM mcr.microsoft.com/windows/servercore:ltsc2022

# Install dependencies like Rust, Node.js, Python/uv via choco or manually
# Note: Building a full Windows UI automation and Tauri app in Docker requires Windows containers
# and considerable setup. This Dockerfile is a stub for the isolated environment.

WORKDIR /app
COPY . .

CMD ["cmd.exe"]