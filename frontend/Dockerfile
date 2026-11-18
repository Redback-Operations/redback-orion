FROM node:20-alpine

WORKDIR /app

# Use the same pnpm version as package.json's "packageManager" field
RUN npm install -g pnpm@10.14.0

# Install from the lockfile so Docker gets the same versions as local dev.
# .npmrc is copied too so its install settings apply here.
COPY package.json pnpm-lock.yaml .npmrc ./

RUN pnpm install --frozen-lockfile

COPY . .

EXPOSE 8080

CMD ["pnpm", "dev", "--host", "0.0.0.0"]
