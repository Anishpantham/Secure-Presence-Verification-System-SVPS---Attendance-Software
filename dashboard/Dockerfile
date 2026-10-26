FROM node:22-alpine AS build
WORKDIR /app/dashboard
COPY dashboard/package.json dashboard/package-lock.json ./
RUN --mount=type=secret,id=ca_bundle \
    if [ -f /run/secrets/ca_bundle ]; then NODE_EXTRA_CA_CERTS=/run/secrets/ca_bundle npm ci; else npm ci; fi
COPY dashboard .
COPY mobile/src/acousticCodec.ts /app/mobile/src/acousticCodec.ts
RUN npm run build
FROM nginx:1.27-alpine
COPY dashboard/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dashboard/dist /usr/share/nginx/html
EXPOSE 80
