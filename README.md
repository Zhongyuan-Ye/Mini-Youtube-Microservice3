# Mini-Youtube-Microservice3
Microservice 3 of the Mini-Youtube Project. Member Service &amp; Administrator Service

Member service (and Administrator serivice) of the Mini-Youtube Project.

upload
curl -X POST "http://ec2-18-219-133-27.us-east-2.compute.amazonaws.com:1024/upload-video/?username=zy2550" -H "accept: application/json" -H "Content-Type: multipart/form-data" -F "file=@C:\Users\zhong\Downloads\video-example\micro3.mp4;type=video/mp4"
