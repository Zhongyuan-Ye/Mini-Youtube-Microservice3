from fastapi import FastAPI, UploadFile, HTTPException, File, Depends
import uvicorn
import sqlite3
import uuid
import requests

app = FastAPI()

# Database Connection
def get_db_connection():
    conn = sqlite3.connect('videos.db')
    conn.row_factory = sqlite3.Row
    return conn

# Initialize Database (Run this once)
def init_db():
    with get_db_connection() as conn:
        conn.execute('''CREATE TABLE videos 
                        (video_id TEXT PRIMARY KEY, 
                         video_name TEXT, 
                         uploader TEXT, 
                         publicity BOOLEAN)''')
        conn.commit()

# Microservice 1 URL
ms1_url = 'ec2-3-140-208-26.us-east-2.compute.amazonaws.com:1024'

@app.get("/fetch-video/{username}/{video_id}")
async def fetch_video(username: str, video_id: str):
    with get_db_connection() as conn:
        video = conn.execute("SELECT * FROM videos WHERE video_id = ?", (video_id,)).fetchone()
        if video and (video['uploader'] == username or video['publicity']):
            response = requests.get(f"{ms1_url}/fetch-video/{video_id}.mp4")
            if response.status_code == 200:
                return response.content
            else:
                raise HTTPException(status_code=response.status_code, detail=response.json())
        else:
            raise HTTPException(status_code=404, detail="Video not found or access denied")
        

@app.get("/find-all-videos/{username}")
async def find_all(username: str):
    with get_db_connection() as conn:
        videos = conn.execute("SELECT * FROM videos WHERE uploader = ?", (username,)).fetchall()
        if videos:
            return [{"video_id": video['video_id'], "video_name": video['video_name']} for video in videos]
        else:
            return {"message": "No video found"}


@app.put("/publish-video/{username}/{video_id}")
def publish_video(username: str, video_id: str):
    with get_db_connection() as conn:
        result = conn.execute("UPDATE videos SET publicity = True WHERE video_id = ? AND uploader = ?", 
                              (video_id, username))
        if result.rowcount == 0:
            return {"message": "Video not found or access denied"}
        conn.commit()
    return {"message": "Video published successfully"}



@app.delete("/delete-video/{username}/{video_id}")
async def delete_video(username: str, video_id: str):
    with get_db_connection() as conn:
        video = conn.execute("SELECT * FROM videos WHERE video_id = ?", (video_id,)).fetchone()
        if video and video['uploader'] == username:
            response = requests.delete(f"{ms1_url}/delete-video/{video_id}.mp4")
            if response.status_code == 200:
                conn.execute("DELETE FROM videos WHERE video_id = ?", (video_id,))
                conn.commit()
                return {"message": "Video deleted successfully"}
            else:
                raise HTTPException(status_code=response.status_code, detail=response.json())
        else:
            raise HTTPException(status_code=404, detail="Video not found or access denied")
        
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=1024)