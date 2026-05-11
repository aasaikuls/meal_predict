# ── Stage 1: Build ──────────────────────────────────────────────────────────
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY config-overrides.js .
COPY postcss.config.js .
COPY tailwind.config.js .
COPY .env* ./
COPY public ./public
COPY src ./src

RUN npm run build

# ── Stage 2: Serve ───────────────────────────────────────────────────────────
FROM node:18-alpine

RUN npm install -g serve

WORKDIR /app
COPY --from=builder /app/build ./build

EXPOSE 3001

CMD ["serve", "-s", "build", "-l", "3001"]
