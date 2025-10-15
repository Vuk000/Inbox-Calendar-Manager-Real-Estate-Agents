# 🚀 RealInbox AI - Deployment Guide

Complete guide for deploying RealInbox AI to production.

---

## Pre-Deployment Checklist

- [ ] All tests passing
- [ ] Environment variables configured
- [ ] API keys obtained (Anthropic, Google, Microsoft, etc.)
- [ ] Database backup strategy in place
- [ ] Monitoring setup (Sentry)
- [ ] Domain name registered
- [ ] SSL certificates configured
- [ ] Rate limiting configured
- [ ] Security audit completed

---

## Option 1: Deploy to AWS (Recommended for Enterprise)

### Architecture

- **Frontend**: Vercel or AWS Amplify
- **Backend API**: AWS ECS (Elastic Container Service)
- **Database**: AWS RDS PostgreSQL
- **Cache**: AWS ElastiCache Redis
- **Storage**: AWS S3
- **Load Balancer**: AWS ALB
- **Workers**: AWS ECS (separate service)

### Steps

#### 1. Setup AWS Infrastructure

```bash
# Install AWS CLI
pip install awscli

# Configure AWS credentials
aws configure
```

#### 2. Create RDS PostgreSQL Database

```bash
# Using AWS Console or CLI
aws rds create-db-instance \
    --db-instance-identifier realinbox-prod-db \
    --db-instance-class db.t3.micro \
    --engine postgres \
    --engine-version 15.3 \
    --master-username admin \
    --master-user-password <strong-password> \
    --allocated-storage 20 \
    --publicly-accessible false \
    --vpc-security-group-ids <sg-id> \
    --db-subnet-group-name <subnet-group>
```

#### 3. Create ElastiCache Redis

```bash
aws elasticache create-cache-cluster \
    --cache-cluster-id realinbox-cache \
    --cache-node-type cache.t3.micro \
    --engine redis \
    --num-cache-nodes 1
```

#### 4. Create S3 Bucket

```bash
aws s3 mb s3://realinbox-documents
aws s3api put-bucket-encryption \
    --bucket realinbox-documents \
    --server-side-encryption-configuration '{
      "Rules": [{
        "ApplyServerSideEncryptionByDefault": {
          "SSEAlgorithm": "AES256"
        }
      }]
    }'
```

#### 5. Build and Push Docker Image

```bash
cd backend

# Build image
docker build -t realinbox-api:latest .

# Tag for ECR
docker tag realinbox-api:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/realinbox-api:latest

# Login to ECR
aws ecr get-login-password --region us-east-1 | \
    docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Push
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/realinbox-api:latest
```

#### 6. Create ECS Cluster and Services

```bash
# Create cluster
aws ecs create-cluster --cluster-name realinbox-prod

# Create task definition (API)
aws ecs register-task-definition --cli-input-json file://ecs-task-api.json

# Create task definition (Workers)
aws ecs register-task-definition --cli-input-json file://ecs-task-workers.json

# Create services
aws ecs create-service \
    --cluster realinbox-prod \
    --service-name realinbox-api \
    --task-definition realinbox-api \
    --desired-count 2 \
    --launch-type FARGATE \
    --load-balancers targetGroupArn=<tg-arn>,containerName=api,containerPort=8000
```

#### 7. Configure Environment Variables in ECS

Use AWS Systems Manager Parameter Store or Secrets Manager:

```bash
aws ssm put-parameter \
    --name /realinbox/prod/database-url \
    --value "postgresql://..." \
    --type SecureString

aws ssm put-parameter \
    --name /realinbox/prod/anthropic-key \
    --value "sk-ant-..." \
    --type SecureString
```

#### 8. Deploy Frontend to Vercel

```bash
cd frontend

# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod

# Set environment variables in Vercel dashboard
# VITE_API_URL=https://api.realinbox.ai/api/v1
```

---

## Option 2: Deploy to Heroku (Quick & Easy)

### Backend

```bash
cd backend

# Login to Heroku
heroku login

# Create app
heroku create realinbox-api

# Add PostgreSQL
heroku addons:create heroku-postgresql:standard-0

# Add Redis
heroku addons:create heroku-redis:premium-0

# Set environment variables
heroku config:set ANTHROPIC_API_KEY=your-key
heroku config:set GOOGLE_CLIENT_ID=your-id
# ... set all required env vars

# Deploy
git push heroku main

# Run migrations
heroku run python -c "from app.db import init_db; init_db()"

# Scale workers
heroku ps:scale web=2 worker=1
```

### Frontend

```bash
cd frontend

# Deploy to Vercel
vercel --prod

# Or deploy to Netlify
npm run build
netlify deploy --prod --dir=dist
```

---

## Option 3: Deploy to Render (Modern Alternative)

### Backend

1. Go to https://render.com
2. Create new Web Service
3. Connect GitHub repository
4. Configure:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 4`
5. Add environment variables
6. Create PostgreSQL database (Render provides this)
7. Create Redis instance
8. Deploy

### Workers

1. Create new Background Worker on Render
2. Start Command: `celery -A app.workers.celery_app worker --loglevel=info`
3. Use same environment variables

### Frontend

Deploy to Vercel or Render static site.

---

## Database Migration

### Production Database Setup

```sql
-- Create database
CREATE DATABASE realinbox_prod;

-- Create user
CREATE USER realinbox_user WITH PASSWORD 'strong-password-here';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE realinbox_prod TO realinbox_user;

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For text search
```

### Run Migrations

```bash
# Using Alembic (optional)
cd backend
alembic upgrade head

# Or using init_db
python -c "from app.db import init_db; init_db()"
```

---

## Environment Variables (Production)

### Critical Security Variables

```env
# Generate strong keys!
SECRET_KEY=<use-secrets.token_urlsafe(32)>
JWT_SECRET_KEY=<use-secrets.token_urlsafe(32)>
ENCRYPTION_KEY=<use-secrets.token_urlsafe(32)>
ENCRYPTION_SALT=<use-secrets.token_urlsafe(16)>
```

### Database URLs

```env
DATABASE_URL=postgresql://user:password@host:5432/dbname
REDIS_URL=redis://host:6379/0
```

### API Keys

```env
ANTHROPIC_API_KEY=sk-ant-your-production-key
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
MICROSOFT_CLIENT_ID=your-microsoft-client-id
MICROSOFT_CLIENT_SECRET=your-microsoft-client-secret
PINECONE_API_KEY=your-pinecone-key
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
STRIPE_API_KEY=your-stripe-key
SENTRY_DSN=your-sentry-dsn
```

### Update Redirect URIs

```env
GOOGLE_REDIRECT_URI=https://api.yourdomain.com/api/v1/integrations/gmail/callback
MICROSOFT_REDIRECT_URI=https://api.yourdomain.com/api/v1/integrations/outlook/callback
```

---

## Post-Deployment

### 1. Verify Health

```bash
curl https://api.yourdomain.com/health
# Should return: {"status": "healthy", ...}
```

### 2. Test Authentication

```bash
# Register test user
curl -X POST https://api.yourdomain.com/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","full_name":"Test User"}'
```

### 3. Monitor Logs

- Check Sentry for errors
- Monitor API response times
- Watch Celery worker logs
- Check database performance

### 4. Setup Monitoring

- Configure alerts for API downtime
- Set up log aggregation (AWS CloudWatch, Logtail)
- Monitor AI API costs
- Track user signup rate

---

## Scaling Considerations

### For 100-500 Users

- 2-3 backend instances
- 1 dedicated worker instance
- Standard RDS instance
- Redis with persistence

### For 500-2000 Users

- 5-10 auto-scaling backend instances
- 2-3 worker instances
- Multi-AZ RDS with read replicas
- Redis cluster

### For 2000+ Users

- Consider microservices architecture
- Database sharding by user_id
- CDN for frontend
- Multi-region deployment

---

## Backup & Disaster Recovery

### Database Backups

```bash
# Automated daily backups (AWS RDS)
aws rds modify-db-instance \
    --db-instance-identifier realinbox-prod-db \
    --backup-retention-period 7 \
    --preferred-backup-window "03:00-04:00"

# Manual backup
pg_dump -h <host> -U <user> -d realinbox_prod > backup.sql
```

### Restore from Backup

```bash
psql -h <host> -U <user> -d realinbox_prod < backup.sql
```

---

## Security Hardening

### 1. Enable HTTPS Only

```python
# In main.py
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
app.add_middleware(HTTPSRedirectMiddleware)
```

### 2. Configure CORS Properly

```env
CORS_ORIGINS=https://app.yourdomain.com
```

### 3. Rate Limiting

```python
# Implement Redis-based rate limiting in production
```

### 4. Database Security

- Use SSL connections
- Restrict access to VPC only
- Regular security patches
- Encrypted at rest and in transit

---

## Cost Optimization

### Monitor Costs

- **Anthropic API**: Cache similar queries, ~$0.02/user/day
- **Database**: Use appropriate instance size
- **S3**: Lifecycle policies for old documents
- **Workers**: Scale down during off-hours

### Target Costs (100 Users)

- Infrastructure: $200-300/month
- AI API: $200-300/month
- Total: $400-600/month
- Revenue (100 × $29): $2,900/month
- **Profit Margin: ~80%**

---

## Monitoring & Alerts

### Setup Sentry

```python
# Already configured in main.py
# Just add SENTRY_DSN to environment
```

### Setup Uptime Monitoring

- Use UptimeRobot or Pingdom
- Monitor: /health endpoint
- Alert on: Downtime > 2 minutes

### Log Aggregation

- AWS CloudWatch Logs
- Or use Papertrail/Logtail
- Set up log retention policies

---

## Domain & DNS

### Configure DNS

```
A     api.yourdomain.com    -> <ALB-IP>
CNAME app.yourdomain.com    -> <vercel-domain>
```

### SSL Certificates

- Use AWS Certificate Manager (free)
- Or Let's Encrypt
- Auto-renewal enabled

---

## Maintenance

### Regular Tasks

- **Daily**: Check error logs, monitor costs
- **Weekly**: Review user feedback, check performance metrics
- **Monthly**: Database optimization, security patches
- **Quarterly**: Security audit, cost review

### Update Deployment

```bash
# Backend
git pull origin main
docker build -t realinbox-api:latest .
docker push <ecr-url>/realinbox-api:latest
aws ecs update-service --cluster realinbox-prod --service realinbox-api --force-new-deployment

# Frontend
cd frontend
git pull origin main
vercel --prod
```

---

**Production Deployment Complete!** 🎉

Your RealInbox AI platform is now live and serving users!

