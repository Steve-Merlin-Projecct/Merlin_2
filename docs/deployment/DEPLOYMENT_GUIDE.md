# Deployment Guide

## Overview

This document provides comprehensive deployment instructions for the Merlin Job Application System across different environments.

**Current Status**: Post-Replit Migration - Platform Agnostic
**Deployment Options**: Local, Docker, Cloud (AWS, GCP, Azure)

---

## Prerequisites

### Required Software
- **Python**: 3.11 or higher
- **PostgreSQL**: 12 or higher
- **Git**: For version control
- **pip**: Python package manager

### Required Accounts & Keys
- Google Gemini API key (AI analysis)
- Apify API token (job scraping)
- Gmail OAuth credentials (email integration)
- PostgreSQL database (local or cloud)

---

## Local Development Deployment

### 1. Clone Repository
```bash
git clone <repository-url>
cd merlin-job-application-system
```

### 2. Environment Setup
```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your credentials
```

### 3. Database Setup
```bash
# Create PostgreSQL database
createdb local_Merlin_3

# Run migrations (if applicable)
# python database_tools/run_migrations.py

# Verify connection
python -c "from modules.database import get_db_session; print('✅ Database connected')"
```

### 4. Start Application
```bash
# Development mode
make serve
# OR
python -m flask --app app_modular run --debug --port 5000

# Production mode (with Gunicorn)
gunicorn --bind 0.0.0.0:5000 --workers 4 app_modular:app
```

### 5. Verify Deployment
```bash
# Run tests
make test

# Check health endpoint
curl http://localhost:5000/health
```

---

## Docker Deployment

### 1. Using Docker Compose (Recommended)
```bash
# Build and start containers
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop containers
docker-compose down
```

### 2. Manual Docker Build
```bash
# Build image
docker build -t merlin-job-app:latest .

# Run container
docker run -d \
  --name merlin-app \
  -p 5000:5000 \
  --env-file .env \
  merlin-job-app:latest

# View logs
docker logs -f merlin-app
```

### 3. Environment Variables in Docker
```bash
# Option 1: Using --env-file
docker run --env-file .env merlin-job-app:latest

# Option 2: Individual -e flags
docker run \
  -e DATABASE_URL=postgresql://... \
  -e GEMINI_API_KEY=... \
  merlin-job-app:latest
```

---

## Cloud Deployment

### AWS Deployment

#### Option 1: AWS Elastic Beanstalk
```bash
# Install EB CLI
pip install awsebcli

# Initialize EB application
eb init -p python-3.11 merlin-job-app

# Create environment
eb create merlin-production

# Deploy
eb deploy

# Set environment variables
eb setenv \
  DATABASE_URL=postgresql://... \
  GEMINI_API_KEY=...

# View logs
eb logs
```

#### Option 2: AWS ECS (Docker)
```yaml
# task-definition.json
{
  "family": "merlin-job-app",
  "containerDefinitions": [{
    "name": "app",
    "image": "your-ecr-repo/merlin-job-app:latest",
    "portMappings": [{
      "containerPort": 5000,
      "protocol": "tcp"
    }],
    "environment": [
      {"name": "DATABASE_HOST", "value": "your-rds-endpoint"},
      {"name": "DATABASE_NAME", "value": "local_Merlin_3"}
    ],
    "secrets": [
      {"name": "DATABASE_PASSWORD", "valueFrom": "arn:aws:secretsmanager:..."}
    ]
  }]
}
```

#### AWS RDS for PostgreSQL
```bash
# Create RDS instance
aws rds create-db-instance \
  --db-instance-identifier merlin-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version 15.3 \
  --master-username postgres \
  --master-user-password <password> \
  --allocated-storage 20

# Get endpoint
aws rds describe-db-instances \
  --db-instance-identifier merlin-db \
  --query 'DBInstances[0].Endpoint.Address'
```

### Google Cloud Platform Deployment

#### Cloud Run (Serverless)
```bash
# Build and push to GCR
gcloud builds submit --tag gcr.io/PROJECT-ID/merlin-job-app

# Deploy to Cloud Run
gcloud run deploy merlin-job-app \
  --image gcr.io/PROJECT-ID/merlin-job-app \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DATABASE_HOST=... \
  --set-secrets DATABASE_PASSWORD=...

# Update service
gcloud run services update merlin-job-app \
  --set-env-vars NEW_VAR=value
```

#### Cloud SQL for PostgreSQL
```bash
# Create Cloud SQL instance
gcloud sql instances create merlin-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1

# Create database
gcloud sql databases create local_Merlin_3 \
  --instance=merlin-db

# Connect Cloud Run to Cloud SQL
gcloud run services update merlin-job-app \
  --add-cloudsql-instances PROJECT-ID:us-central1:merlin-db
```

### Azure Deployment

#### Azure App Service
```bash
# Create resource group
az group create --name merlin-rg --location eastus

# Create App Service plan
az appservice plan create \
  --name merlin-plan \
  --resource-group merlin-rg \
  --sku B1 \
  --is-linux

# Create web app
az webapp create \
  --resource-group merlin-rg \
  --plan merlin-plan \
  --name merlin-job-app \
  --runtime "PYTHON:3.11"

# Deploy code
az webapp up --name merlin-job-app

# Set environment variables
az webapp config appsettings set \
  --resource-group merlin-rg \
  --name merlin-job-app \
  --settings DATABASE_URL=...
```

---

## Environment-Specific Configuration

### Development
```bash
# .env.development
FLASK_ENV=development
FLASK_DEBUG=True
LOG_LEVEL=DEBUG
DATABASE_URL=postgresql://localhost/local_Merlin_3
STORAGE_BACKEND=local
```

### Staging
```bash
# .env.staging
FLASK_ENV=production
FLASK_DEBUG=False
LOG_LEVEL=INFO
DATABASE_URL=postgresql://staging-db/local_Merlin_3
STORAGE_BACKEND=s3
S3_BUCKET_NAME=merlin-staging-storage
```

### Production
```bash
# .env.production
FLASK_ENV=production
FLASK_DEBUG=False
LOG_LEVEL=WARNING
DATABASE_URL=postgresql://prod-db/local_Merlin_3
STORAGE_BACKEND=s3
S3_BUCKET_NAME=merlin-production-storage
ENABLE_ERROR_REPORTING=True
```

---

## Post-Deployment Checklist

### Immediate After Deployment
- [ ] Verify health endpoint responds: `curl https://your-domain/health`
- [ ] Check database connectivity
- [ ] Verify environment variables are loaded
- [ ] Test document generation endpoint
- [ ] Test job scraping functionality
- [ ] Check AI analysis integration

### Within 24 Hours
- [ ] Monitor error logs
- [ ] Check application metrics (CPU, memory, requests)
- [ ] Verify scheduled jobs are running (if applicable)
- [ ] Test email sending functionality
- [ ] Review security scan results

### Within 1 Week
- [ ] Load testing
- [ ] Database performance tuning
- [ ] Set up monitoring dashboards
- [ ] Configure automated backups
- [ ] Document any deployment issues

---

## Monitoring & Maintenance

### Health Checks
```python
# Health endpoint: /health
{
  "status": "healthy",
  "database": "connected",
  "storage": "accessible",
  "ai_service": "available"
}
```

### Logging
```bash
# View application logs
# Local
tail -f logs/application.log

# Docker
docker logs -f merlin-app

# Cloud Run
gcloud run services logs tail merlin-job-app

# AWS ECS
aws logs tail /ecs/merlin-job-app --follow
```

### Database Backups
```bash
# Local backup
pg_dump local_Merlin_3 > backup_$(date +%Y%m%d).sql

# Restore
psql local_Merlin_3 < backup_20250101.sql

# AWS RDS automated backups
aws rds create-db-snapshot \
  --db-instance-identifier merlin-db \
  --db-snapshot-identifier merlin-backup-$(date +%Y%m%d)

# GCP Cloud SQL backups
gcloud sql backups create \
  --instance=merlin-db
```

---

## Scaling

### Horizontal Scaling
```bash
# Docker Compose
docker-compose up --scale app=3

# Kubernetes
kubectl scale deployment merlin-app --replicas=3

# AWS ECS
aws ecs update-service \
  --cluster merlin-cluster \
  --service merlin-service \
  --desired-count 3
```

### Database Connection Pooling
```python
# In database configuration
SQLALCHEMY_POOL_SIZE = 10
SQLALCHEMY_MAX_OVERFLOW = 20
SQLALCHEMY_POOL_TIMEOUT = 30
SQLALCHEMY_POOL_RECYCLE = 1800
```

---

## Troubleshooting

### Common Deployment Issues

#### Database Connection Failures
```bash
# Check database is running
pg_isready -h localhost -p 5432

# Verify credentials
psql postgresql://user:password@host:5432/database

# Check firewall rules (cloud)
# AWS: Security groups
# GCP: VPC firewall rules
```

#### Application Won't Start
```bash
# Check Python version
python --version  # Should be 3.11+

# Verify dependencies
pip list

# Check environment variables
env | grep DATABASE_URL

# Review logs
tail -f logs/application.log
```

#### Storage Issues
```bash
# Verify storage directory exists and is writable
ls -la storage/
chmod 755 storage/

# Test storage backend
python -c "from modules.storage import get_storage_client; client = get_storage_client(); print('✅ Storage OK')"
```

---

## Security Considerations

### Environment Variables
- **Never** commit `.env` files
- Use secret management services in production:
  - AWS Secrets Manager
  - GCP Secret Manager
  - Azure Key Vault
  - HashiCorp Vault

### Database Security
- Use SSL/TLS for database connections
- Restrict database access by IP
- Use strong passwords
- Enable automated backups

### Application Security
- Keep dependencies updated: `pip list --outdated`
- Run security scans: `pip-audit`
- Enable HTTPS in production
- Implement rate limiting
- Configure CORS properly

---

## Rollback Procedures

### Docker Deployment
```bash
# Tag current version
docker tag merlin-job-app:latest merlin-job-app:v1.0.0

# Rollback to previous version
docker stop merlin-app
docker run -d merlin-job-app:v0.9.0
```

### Cloud Deployments
```bash
# AWS Elastic Beanstalk
eb deploy --version <previous-version>

# GCP Cloud Run
gcloud run services update merlin-job-app \
  --image gcr.io/PROJECT-ID/merlin-job-app:previous-tag

# Azure App Service
az webapp deployment slot swap \
  --resource-group merlin-rg \
  --name merlin-job-app \
  --slot staging \
  --target-slot production
```

---

## Support & Resources

### Internal Documentation
- [CLAUDE.md](../../CLAUDE.md) - Project overview
- [Database Schema](../component_docs/database/database_schema.md)
- [API Documentation](../development/API_DOCUMENTATION.md)

### External Resources
- [Flask Deployment](https://flask.palletsprojects.com/en/latest/deploying/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Documentation](https://docs.docker.com/)

---

**Document Version**: 1.0
**Last Updated**: October 2025
**Maintained By**: Development Team
