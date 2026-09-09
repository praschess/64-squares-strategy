#!/usr/bin/env bash
set -euo pipefail
REGION="${AWS_REGION:-us-west-2}"
STACK="${STACK_NAME:-64-squares-strategy-rag}"
ORIGIN="${ALLOWED_ORIGIN:-https://praschess.github.io}"
echo "Deploying $STACK in $REGION..."
sam build
sam deploy --stack-name "$STACK" --region "$REGION" --resolve-s3 --capabilities CAPABILITY_IAM --parameter-overrides "AllowedOrigin=$ORIGIN" --no-confirm-changeset
BUCKET="$(aws cloudformation describe-stacks --stack-name "$STACK" --region "$REGION" --query "Stacks[0].Outputs[?OutputKey=='KnowledgeBucketName'].OutputValue" --output text)"
KB_ID="$(aws cloudformation describe-stacks --stack-name "$STACK" --region "$REGION" --query "Stacks[0].Outputs[?OutputKey=='KnowledgeBaseId'].OutputValue" --output text)"
DS_ID="$(aws cloudformation describe-stacks --stack-name "$STACK" --region "$REGION" --query "Stacks[0].Outputs[?OutputKey=='DataSourceId'].OutputValue" --output text)"
API_URL="$(aws cloudformation describe-stacks --stack-name "$STACK" --region "$REGION" --query "Stacks[0].Outputs[?OutputKey=='ChatApiUrl'].OutputValue" --output text)"
aws s3 sync knowledge/ "s3://$BUCKET/knowledge/" --delete --region "$REGION"
JOB_ID="$(aws bedrock-agent start-ingestion-job --knowledge-base-id "$KB_ID" --data-source-id "$DS_ID" --region "$REGION" --query "ingestionJob.ingestionJobId" --output text)"
echo "Ingestion job: $JOB_ID"
echo "Chat API URL: $API_URL"
echo "Next: ./scripts/configure-frontend.sh '$API_URL'"
