from config_lib import Config, ConfigError

def main():
    # Create or open settings.json, autosave True by default
    cfg = Config("settings.json", autosave=True)

    # Simple assignment at top level
    cfg.app_name = "MyApp"
    cfg.version = 1.0

    # Nested categories via attribute access
    cfg.server.host = "127.0.0.1"
    cfg.server.port = 8080

    # Even deeper nesting
    cfg.database.credentials.user = "admin"
    cfg.database.credentials.password = "s3cret"

    # You can also use dict-style access for keys that are not valid identifiers
    cfg["some-key"] = {"complex": [1, 2, 3]}

    # Read values
    print("App:", cfg.app_name)                # MyApp
    print("Server port:", cfg.server.port)     # 8080
    print("DB user:", cfg.database.credentials.user)  # admin

    # Use to_dict() to get a plain dict
    data = cfg.to_dict()
    print("Full config as dict:", data)

    # Delete a key
    del cfg.version

    # Reload from disk (if you edited the file externally)
    cfg.reload()

    # Use as context manager (saves on exit if autosave=False)
    with Config("temp_cfg.json", autosave=False) as c:
        c.example = True
        c.nested.value = 42
        # when exiting the with-block, temp_cfg.json will be saved

if __name__ == "__main__":
    try:
        main()
    except ConfigError as e:
        print("Configuration error:", e)
