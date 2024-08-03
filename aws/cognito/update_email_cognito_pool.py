import boto3

client = boto3.client('cognito-idp')


const params = {
  UserPoolId: 'us-east-1_KwxhorJ3L',
  Username: 'username',
  UserAttributes: [
    {
      Name: "email",
      Value: "new email"
    },
    {
      Name: "email_verified",
      Value: "false"
    }
  ],
};
const cognitoClient = new AWS.CognitoIdentityServiceProvider();
const createPromise = cognitoClient.adminUpdateUserAttributes(params).promise();
await createPromise;