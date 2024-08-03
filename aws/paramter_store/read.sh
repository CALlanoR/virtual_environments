export DATABASE_HOST=$(aws ssm get-parameters --names HEALTHNEXUS_CODEGROUPS_API_DB_HOST_DEV --query Parameters[0].Value | sed 's/"//g')
echo $DATABASE_HOST