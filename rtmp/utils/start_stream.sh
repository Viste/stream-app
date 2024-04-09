#!/bin/bash

COURSE_NAME=$1
IS_LIVE=true

curl -X POST http://academy-service.stream.svc.pprfnk.local/api/update_status \
     -H "Content-Type: application/json" \
     -d "{\"short_name\":\"$COURSE_NAME\", \"is_live\":$IS_LIVE}"