#!/bin/bash

# ----------------------------------------
# AWS Secrets Manager secret name
# ----------------------------------------
SECRET_NAME="meal_predict"

# ----------------------------------------
# Helper: copy .env.example → .env if missing
# ----------------------------------------
setup_env() {
    local src="$1"
    local dst="$2"
    if [ ! -f "$dst" ]; then
        echo "Creating $dst from $src..."
        cp "$src" "$dst"
    else
        echo "$dst already exists, skipping copy."
    fi
}

# ----------------------------------------
# Helper: update or append KEY=VALUE in file
# ----------------------------------------
inject_secret() {
    local file="$1"
    local key="$2"
    local value="$3"
    if [ -z "$value" ] || [ "$value" = "null" ]; then
        echo "  WARNING: empty value for $key — skipping (set it manually in $file)"
        return
    fi
    if grep -q "^${key}=" "$file"; then
        sed -i "s|^${key}=.*|${key}=${value}|" "$file"
    else
        echo "${key}=${value}" >> "$file"
    fi
    echo "  Updated ${key} in $file"
}

# ----------------------------------------
# Step 1: Set up .env files from examples
# ----------------------------------------
echo ""
echo "========================================"
echo "Setting up .env files"
echo "========================================"
setup_env "backend/.env.example"  "backend/.env"
setup_env "frontend/.env.example" "frontend/.env"

# ----------------------------------------
# Step 2: Inject secrets from AWS Secrets Manager
# ----------------------------------------
if command -v aws &>/dev/null && command -v jq &>/dev/null; then
    echo ""
    echo "Fetching secrets from AWS Secrets Manager ($SECRET_NAME)..."
    SECRET_JSON=$(aws secretsmanager get-secret-value \
        --secret-id "$SECRET_NAME" \
        --query SecretString \
        --output text 2>/dev/null)
    if [ -z "$SECRET_JSON" ]; then
        echo "  ERROR: Could not retrieve secret '$SECRET_NAME'. Check AWS credentials and secret name."
    else
        inject_secret "backend/.env" "MYSQL_HOST"     "$(echo "$SECRET_JSON" | jq -r '.MYSQL_HOST')"
        inject_secret "backend/.env" "MYSQL_PORT"     "$(echo "$SECRET_JSON" | jq -r '.MYSQL_PORT')"
        inject_secret "backend/.env" "MYSQL_DATABASE" "$(echo "$SECRET_JSON" | jq -r '.MYSQL_DATABASE')"
        inject_secret "backend/.env" "MYSQL_USER"     "$(echo "$SECRET_JSON" | jq -r '.MYSQL_USER')"
        inject_secret "backend/.env" "MYSQL_PASSWORD" "$(echo "$SECRET_JSON" | jq -r '.MYSQL_PASSWORD')"
        inject_secret "backend/.env" "LLM_USER_TOKEN" "$(echo "$SECRET_JSON" | jq -r '.LLM_USER_TOKEN')"
    fi
elif ! command -v aws &>/dev/null; then
    echo ""
    echo "AWS CLI not found — skipping Secrets Manager fetch."
    echo "Please set DB credentials and LLM_USER_TOKEN manually in backend/.env"
elif ! command -v jq &>/dev/null; then
    echo ""
    echo "jq not found — skipping Secrets Manager fetch. Install jq and re-run."
    echo "Please set DB credentials and LLM_USER_TOKEN manually in backend/.env"
fi

echo ""
echo "========================================"
echo "Starting Backend Server (FastAPI in venv)"
echo "========================================"
cd backend
chmod +x start-backend.sh
./start-backend.sh &
BACKEND_PID=$!
sleep 5

echo ""
echo "========================================"
echo "Starting Frontend Server (React)"
echo "========================================"
cd ../frontend
PORT=3001 npm start &
FRONTEND_PID=$!

echo ""
echo "========================================"
echo "Servers are running..."
echo "Backend: http://localhost:8001"
echo "Frontend: http://localhost:3001"
echo "========================================"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for user interrupt
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
