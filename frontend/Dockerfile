FROM node:16-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install --legacy-peer-deps
COPY . .
RUN CI=false npm run build --legacy-peer-deps

FROM nginx:1.25.4-alpine
COPY --from=builder /app/build /var/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]