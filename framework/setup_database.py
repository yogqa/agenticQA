
import subprocess
import time
import os
import sys

# Configuration matches mcp_config.py
CONTAINER_NAME = "mysql-agentic"
MYSQL_PORT = "3306"
MYSQL_PASSWORD = "mypassword"
SQL_FILE_PATH = os.path.join(os.path.dirname(__file__), "resources", "db_script_data.sql")

def run_cmd(cmd, check=True):
    """Run a shell command."""
    print(f"Running: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=check, text=True, capture_output=True)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e.cmd}")
        print(f"Stderr: {e.stderr}")
        if check:
            sys.exit(1)
        return e

def is_mysql_ready():
    """Check if MySQL is ready to accept connections."""
    check_cmd = f"docker exec {CONTAINER_NAME} mysqladmin ping -h localhost -u root --password={MYSQL_PASSWORD} --silent"
    result = run_cmd(check_cmd, check=False)
    return result.returncode == 0

def main():
    print("=== Automating Database Setup ===")

    # 1. Cleanup existing container
    print("Checking for existing container...")
    run_cmd(f"docker stop {CONTAINER_NAME}", check=False)
    run_cmd(f"docker rm {CONTAINER_NAME}", check=False)

    # 2. Start new container
    print(f"Starting new MySQL container '{CONTAINER_NAME}'...")
    start_cmd = (
        f"docker run -d -p {MYSQL_PORT}:3306 --name {CONTAINER_NAME} "
        f"-e MYSQL_ROOT_PASSWORD={MYSQL_PASSWORD} mysql:latest"
    )
    run_cmd(start_cmd)

    # 3. Wait for Readiness
    print("Waiting for MySQL to initialize (this may take a few seconds)...")
    attempts = 0
    max_attempts = 30
    while not is_mysql_ready():
        time.sleep(2)
        attempts += 1
        print(".")
        if attempts >= max_attempts:
            print("Timeout waiting for MySQL to start.")
            sys.exit(1)
    print("\nMySQL is UP and READY!")

    # 4. Seed Data
    print(f"Seeding data from {SQL_FILE_PATH}...")
    if not os.path.exists(SQL_FILE_PATH):
        print(f"Error: SQL file not found at {SQL_FILE_PATH}")
        sys.exit(1)

    # Read SQL file content
    with open(SQL_FILE_PATH, 'r') as f:
        sql_content = f.read()

    # Apply SQL via docker exec
    # We pipe content to docker exec -i
    try:
        load_cmd = f"docker exec -i {CONTAINER_NAME} mysql -u root --password={MYSQL_PASSWORD}"
        process = subprocess.run(
            load_cmd,
            input=sql_content,
            text=True,
            shell=True,
            capture_output=True
        )
        if process.returncode != 0:
            print(f"Failed to import SQL: {process.stderr}")
            sys.exit(1)
        
        print("Database successfully seeded with schema and data!")
        print("You can now run the agents.")
        
    except Exception as e:
        print(f"Exception during data seeding: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
