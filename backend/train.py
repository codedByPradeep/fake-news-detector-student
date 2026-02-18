from models import FakeNewsClassifier
import os

if __name__ == "__main__":
    classifier = FakeNewsClassifier()
    # Ensure data directory exists and has sample data
    data_path = os.path.join(os.path.dirname(__file__), "data", "fake_news.csv")
    if os.path.exists(data_path):
        classifier.train(data_path)
    else:
        print(f"Data file not found at {data_path}. Please place your dataset there.")
