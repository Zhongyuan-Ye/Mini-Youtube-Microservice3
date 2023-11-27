# Mini-Youtube-Microservice3
Microservice 3 of the Mini-Youtube Project. Member Service &amp; Administrator Service

Member service (and Administrator serivice) of the Mini-Youtube Project.

upload

curl -X POST "http://ec2-18-219-133-27.us-east-2.compute.amazonaws.com:1024/upload-video/?username=zy2550" -H "accept: application/json" -H "Content-Type: multipart/form-data" -F "file=@C:\Users\zhong\Downloads\video-example\micro3.mp4;type=video/mp4"

find-all
"curl http://ec2-18-219-133-27.us-east-2.compute.amazonaws.com:1024/find-all-videos/zy2550"

publish

"curl -X PUT "http://ec2-18-219-133-27.us-east-2.compute.amazonaws.com:1024/publish-video/zy2550/63ae25db-8510-4017-99d7-80c0cbab4c2c""

fetch

"curl -X GET "http://ec2-18-219-133-27.us-east-2.compute.amazonaws.com:1024/fetch-video/zy2550/63ae25db-8510-4017-99d7-80c0cbab4c2c""

Delete

"curl -X DELETE "http://ec2-18-219-133-27.us-east-2.compute.amazonaws.com:1024/delete-video/zy2550/63ae25db-8510-4017-99d7-80c0cbab4c2c""
