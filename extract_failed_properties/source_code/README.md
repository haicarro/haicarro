# How to build lambda package.

**1.1 Build lambda package for inspection file**
```
sh build_inspection_package.sh
```
**1.2 Build lambda package for listing file**
```
sh build_listing_package.sh
```

# How to deploy with lambda.
**1.1 Deploy for inspection file**

Step 1: upload the "inspection-file-deployment-package.zip" zip file to lambda.

Step 2: setup variable environtment for the database credentials.
```
DB_HOST	<host name of db>
DB_NAME	<database name>
DB_PASS	<password>
DB_PORT	<port>
DB_USER	<user name>
```

Step 3: Setup VPC.
```
VPC: vpc-09f9bd100046ffce6
Subnets: subnet-0d06a04f264df3499
Security groups: sg-03226565a1f8ae8e1
```

Step 4: Setup runtime
```
Runtime: python3.8
Handler: inspection_files.lambda_handler
```

Step 5: Timeout
```
Timeout: 5min
RAM: 9G
```

**1.2 How to test**

Step 1: Hit on the "Test" button for testing and then lambda will return file name.

Step 2: go to s3 bucket and check if this file is existing?

**1.3 Deploy for listing file**

Step 1: upload the "listing-file-deployment-package.zip" zip file to lambda.

Step 2: setup variable environtment for the database credentials.
```
DB_HOST	<host name of db>
DB_NAME	<database name>
DB_PASS	<password>
DB_PORT	<port>
DB_USER	<user name>
```

Step 3: Setup VPC.
```
VPC: vpc-09f9bd100046ffce6
Subnets: subnet-0d06a04f264df3499
Security groups: sg-03226565a1f8ae8e1
```

Step 4: Setup runtime
```
Runtime: python3.8
Handler: listing_files.lambda_handler
```

Step 5: Timeout
```
Timeout: 5min
RAM: 9G
```

**1.4 How to test**

Step 1: Hit on the "Test" button for testing and then lambda will return file name.

Step 2: go to s3 bucket and check if this file is existing?

**1.5 Lambda applications**

https://ap-southeast-1.console.aws.amazon.com/lambda/home?region=ap-southeast-1#/functions/listing_files_engine_audio?tab=code

https://ap-southeast-1.console.aws.amazon.com/lambda/home?region=ap-southeast-1#/functions/inspection_files_engine_audio?tab=code

