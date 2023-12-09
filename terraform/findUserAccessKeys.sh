# Find Terraform user's Access Key : Secret in a TF State 'tf state pull > state.json'
# Change string 'USER_STARTS_WITH' with the beginning of the user name.

jq '.resources[] | select( .type=="aws_iam_access_key" ) | .instances[0].attributes | select(.user | startswith("USER_STARTS_WITH")) | { user: .user, tokens: { id: .id, secret: .secret } } ' state.json
