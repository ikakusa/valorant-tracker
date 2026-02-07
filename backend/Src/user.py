class User:
    required_keys = ["country", "sub", "email_verified", "phone_number_verified", "preferred_username", "player_locale", "acct", "username"]
    def __init__(self, json: dict):
        for key in self.required_keys:
            if json.get(key) is None:
                raise ValueError(f"Invalid User Json: missing '{key}'")
        
        for k in self.required_keys:
            setattr(self, k, json[k])

        self.skin = None
    
    def get_name(self) -> str:
        return self.acct["game_name"]
    
    def get_tagline(self) -> str:
        return self.acct["tag_line"]
    
    def get_fullname(self) -> str:
        return f"{self.get_name()}#{self.get_tagline()}"
    
    def get_puid(self) -> str:
        return self.sub