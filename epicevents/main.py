from utils.database_initializer import DatabaseInitializer
import sentry_sdk

def main():
    try:
        initializer = DatabaseInitializer()
        initializer.initialize()
    except Exception as e:
        sentry_sdk.capture_exception(e)
        print(f"Error during database initialization: {e}")

if __name__ == "__main__":
    main()