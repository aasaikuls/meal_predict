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
# Step 1: Set up root .env from example
# (docker-compose uses this for all services
#  including DB credentials and frontend theme)
# ----------------------------------------
echo ""
echo "========================================"
echo "Setting up .env file"
echo "========================================"
setup_env ".env.example" ".env"

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
        inject_secret ".env" "MYSQL_HOST"     "$(echo "$SECRET_JSON" | jq -r '.MYSQL_HOST')"
        inject_secret ".env" "MYSQL_PORT"     "$(echo "$SECRET_JSON" | jq -r '.MYSQL_PORT')"
        inject_secret ".env" "MYSQL_DATABASE" "$(echo "$SECRET_JSON" | jq -r '.MYSQL_DATABASE')"
        inject_secret ".env" "MYSQL_USER"     "$(echo "$SECRET_JSON" | jq -r '.MYSQL_USER')"
        inject_secret ".env" "MYSQL_PASSWORD" "$(echo "$SECRET_JSON" | jq -r '.MYSQL_PASSWORD')"
        inject_secret ".env" "LLM_USER_TOKEN" "$(echo "$SECRET_JSON" | jq -r '.LLM_USER_TOKEN')"
    fi
elif ! command -v aws &>/dev/null; then
    echo ""
    echo "AWS CLI not found — skipping Secrets Manager fetch."
    echo "Please set DB credentials and LLM_USER_TOKEN manually in .env"
elif ! command -v jq &>/dev/null; then
    echo ""
    echo "jq not found — skipping Secrets Manager fetch. Install jq and re-run."
    echo "Please set DB credentials and LLM_USER_TOKEN manually in .env"
fi

echo ""
echo "========================================"
echo "Building and Starting Docker Containers"
echo "========================================"
echo ""

# Read LOG_DRIVER from .env (strip inline comments and whitespace)
LOG_DRIVER=$(grep -E '^LOG_DRIVER=' .env 2>/dev/null | head -1 | cut -d'=' -f2 | sed 's/[[:space:]]*#.*//' | tr -d '[:space:]')
LOG_DRIVER=${LOG_DRIVER:-json}

if [ "$LOG_DRIVER" = "awslogs" ]; then
    echo "Log driver: awslogs (CloudWatch)"
    COMPOSE_FILES="-f docker-compose.yml -f docker-compose.logging-awslogs.yml"
else
    echo "Log driver: json-file (local)"
    COMPOSE_FILES="-f docker-compose.yml -f docker-compose.logging-json.yml"
fi

docker-compose $COMPOSE_FILES up --build -d

echo ""
echo "========================================"
echo "Containers stopped"
echo "========================================"
echo ""
echo "To start in background: docker-compose $COMPOSE_FILES up -d"
echo "To view logs: docker-compose logs -f"
echo "To stop: docker-compose down"
echo ""
echo "Backend: http://localhost:8001"
echo "Frontend: http://localhost:3001"
echo "========================================"
