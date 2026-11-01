from app.database import Base, engine
import app.models

def main():
    Base.metadata.create_all(engine)
    
    
if __name__ == "__main__":
    main()