
curl -k -u "$ACCESS_KEY:$SECRET_KEY" \
  -X POST "$RANCHER_URL/v3/clusterroletemplatebindings" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "u-jbwtc",
    "roleTemplateId": "rt-5xs49",
    "clusterId": "local",
    "annotations": {
      "rancher.io/tempbind": "true",
      "rancher.io/tempbind-start": "2025-05-13T10:00:00Z",
      "rancher.io/tempbind-duration-minutes": "1"
    }
  }'


