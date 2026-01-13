from src.ui.cli.interface import CLIInterface
from src.config.settings import settings


def main() -> None:
    try:
        if settings.app.debug:
            print(f"Starting {settings.app.app_name} v{settings.app.version}")
            print(f"Environment: {settings.app.environment}")
        
        interface = CLIInterface()
        interface.start()
        
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        raise


if __name__ == "__main__":
    main()
