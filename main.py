from app.core.system import create_system


def main() -> None:
    system = create_system()
    print(system.summary())


if __name__ == "__main__":
    main()
