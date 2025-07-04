#!/bin/bash

# 取得 AWS 帳號別名，默認為 "default"
AWS_PROFILE="default"

# 解析命令行选项
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -a|--account) AWS_PROFILE="$2"; REGION=$(aws configure get region --profile "$2"); shift ;; # 指定 AWS 帳號；重新取得該帳號 region
        *) echo "未知选项: $1"; exit 1 ;;  # 处理未知选项
    esac
    shift
done

aws lambda update-function-configuration --function-name x-career-bff-dev-app --environment --profile $AWS_PROFILE "Variables={
DEFAULT_LANGUAGE=zh_TW,
STAGE=dev,
TESTING=dev,
XC_BUCKET=x-career-bff-dev-serverlessdeploymentbucket-zndkgowobwsz,
XC_USER_BUCKET=x-career-multimedia,
REGION_HOST_AUTH=https://d11k5l9gl6.execute-api.ap-northeast-1.amazonaws.com/dev/auth-service/api,
REGION_HOST_USER=https://gvjbxpuqmh.execute-api.ap-northeast-1.amazonaws.com/dev/user-service/api,
REGION_HOST_SEARCH=https://qa9af3a6vf.execute-api.ap-northeast-1.amazonaws.com/dev/search-service/api,
BATCH=10,
REQUEST_INTERVAL_TTL=8,
SHORT_TERM_TTL=1800,
LONG_TERM_TTL=259200,
JWT_ALGORITHM=HS256,
ACCESS_TOKEN_TTL=1800,
REFRESH_TOKEN_TTL=2592000,
AUTH_RESPONSE_FIELDS=oauth_id;email;account_type;region;online,
CACHE_TTL=300,
TABLE_CACHE=dev_x_career_bff_cache,
AUTH_SERVICE_URL=https://d11k5l9gl6.execute-api.ap-northeast-1.amazonaws.com/dev/auth-service/api,
USER_SERVICE_URL=https://gvjbxpuqmh.execute-api.ap-northeast-1.amazonaws.com/dev/user-service/api,
SEARCH_SERVICE_URL=https://qa9af3a6vf.execute-api.ap-northeast-1.amazonaws.com/dev/search-service/api,
MAX_WIDTH=300,
MAX_HEIGHT=300,
MAX_STORAGE_SIZE=15728640,
}"
