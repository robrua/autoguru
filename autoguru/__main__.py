
import uvicorn

if __name__ == "__main__":
    uvicorn.run("autoguru.main:app", debug=True, reload=True)
