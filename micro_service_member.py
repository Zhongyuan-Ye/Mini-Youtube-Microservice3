from fastapi import FastAPI, UploadFile, HTTPException, File
import uvicorn


from fastapi.responses import StreamingResponse
from databases import Database
import uuid
import requests

app = FastAPI()

# Database URL (SQLite in this case, but you can use other databases)
DATABASE_URL = "sqlite:///./videos.db"
database = Database(DATABASE_URL)

# Initialize Database (Run this once)
async def init_db():
    query = """CREATE TABLE IF NOT EXISTS videos 
               (video_id TEXT PRIMARY KEY, 
                video_name TEXT, 
                uploader TEXT, 
                publicity BOOLEAN)"""
    await database.execute(query)

@app.on_event("startup")
async def startup():
    await database.connect()
    await init_db()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# Microservice 1 URL
ms1_url = 'http://ec2-3-16-13-173.us-east-2.compute.amazonaws.com:1024'

@app.post("/upload-video/")
async def upload_video(username: str, file: UploadFile = File(...)):
    if username != "not_login":
        new_video_id = str(uuid.uuid4())
        new_file_name = f"{new_video_id}.mp4"
    
        # Calling Microservice 1 to upload the video
        response = requests.post(f"{ms1_url}/upload-video/", files={"file": (new_file_name, file.file)})
    
        if response.status_code == 200:
            query = "INSERT INTO videos (video_id, video_name, uploader, publicity) VALUES (:video_id, :video_name, :uploader, :publicity)"
            values = {"video_id": new_video_id, "video_name": file.filename, "uploader": username, "publicity": False}
            await database.execute(query=query, values=values)
            return {"message": "Success", "upload_unique_video_id": new_video_id}
        else:
            raise HTTPException(status_code=response.status_code, detail=response.json())
    else:
        return {"message": "Please login"}


@app.get("/fetch-video/{username}/{video_id}")
async def fetch_video(username: str, video_id: str):
    if username != "not_login":
        query = "SELECT * FROM videos WHERE video_id = :video_id"
        video = await database.fetch_one(query=query, values={"video_id": video_id})
        if video and (video['uploader'] == username or video['publicity']):
            response = requests.get(f"{ms1_url}/fetch-video/{video_id}.mp4", stream=True)
            if response.status_code == 200:
                return StreamingResponse(response.iter_content(chunk_size=1024*1024), media_type="video/mp4")
            else:
                raise HTTPException(status_code=response.status_code, detail="Error fetching video")
        else:
            raise HTTPException(status_code=404, detail="Video not found or access denied")


@app.get("/weather/nyc")
async def get_weather_nyc():

    response = requests.get("https://api.openweathermap.org/data/3.0/onecall?lat=40.71&lon=-74.00&appid=?????????")
    if response.status_code == 200:
        return response
    else:
        raise HTTPException(status_code=response.status_code, detail="Error fetching weather data")


@app.delete("/delete-video/{username}/{video_id}")
async def delete_video(username: str, video_id: str):
    query = "SELECT * FROM videos WHERE video_id = :video_id"
    video = await database.fetch_one(query=query, values={"video_id": video_id})
    if video and video['uploader'] == username:
        response = requests.delete(f"{ms1_url}/delete-video/{video_id}.mp4")
        if response.status_code == 200:
            delete_query = "DELETE FROM videos WHERE video_id = :video_id"
            await database.execute(query=delete_query, values={"video_id": video_id})
            return {"message": "Video deleted successfully"}
        else:
            raise HTTPException(status_code=response.status_code, detail=response.json())
    else:
        raise HTTPException(status_code=404, detail="Video not found or access denied")


@app.put("/publish-video/{username}/{video_id}")
def publish_video(username: str, video_id: str):
    query = "UPDATE videos SET publicity = True WHERE video_id = :video_id AND uploader = :uploader"
    values = {"video_id": video_id, "uploader": username}

    # Running the database operation in a separate thread
    result = database.fetch_one(query=query, values=values)
    if result:
        return {"message": "Video published successfully"}
    else:
        return {"message": "Video not found or access denied"}



@app.get("/find-all-videos/{username}")
async def find_all(username: str):
    query =  """SELECT video_id, video_name, publicity  FROM videos WHERE uploader = :username ORDER BY video_name """
    videos = await database.fetch_all(query=query, values={"username": username})

    def get_imgage(video_ide):
        req_url = str(ms1_url)+"/get-video-image/"+str(video_ide)
        response_current = requests.get(req_url)
        return response_current.json()["image"]

    if videos:
        return [{"video_id": video['video_id'], "video_name": video['video_name'], "publicity": video['publicity'], "video_link": str(ms1_url)+str("/fetch-video/")+video['video_id']+str(".mp4"), "video_image": get_imgage(video['video_id']) } for video in videos]
    else:
        return {"message": "No video found"}


        
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=1024)
