import dataclasses



def handle_auto_debuffs(*args, **kwargs):
    pass
    

debuff_mapping = {
    "poison": 0.5,
    "burn": 0.7,
    "freeze": 0.3,
    "stun": 0.0,
    "slow": 0.8,
    "blind": 0.9,
    "auto": handle_auto_debuffs
}




@dataclasses.dataclass()
class Settings:
    name: str

    level: int = 1
    health: float = 100.0
    is_alive: bool = True
    debuffs: list = dataclasses.field(default_factory=list)

    def activate_debuff(self, debuff: str):
        self.debuffs.append(debuff)


if __name__ == "__main__":

    character = Settings(name="Razza")

    print(character)

