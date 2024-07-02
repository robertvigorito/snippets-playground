

# How to hash a dictionary
from dataclasses import dataclass, field
from typing import Dict, List, Union

from rifs.core import AbstractRif


@dataclass
class HashableRif(AbstractRif):
    """A hashable rif object."""
    subject: str = "world"
    body: str = "Hello, {subject}!"
    send_too: List[str] = field(default_factory=lambda: ["me", "you"])

    
    def post_process(self):
        print("Post process")
        return True
    
    def pre_process(self):
        print("Pre process")
        return True
    

    # def __call__(self, *args, **kwargs) -> None:
    #     # Print subject
    #     super().__call__(*args, **kwargs)
    #     self.pre_process()
    #     print(self.subject)
    #     print(self.body.format(subject=self.subject))
        
    #     print("Sending to:" + ", ".join(self.send_too))
    #     self.post_process()

        
    
class HashableRifChild(HashableRif):
    """A hashable rif object."""
    subject: str = "world"
    body: str = "Hello, {subject}!"
    send_too: list = ["me", "you"]
    

@dataclass
class MyBaseClass:
    value: Union[str, int] = "10"


    def __hash__(self) -> int:
        return hash(str(self.value))

@dataclass()
class MySubclass(MyBaseClass):
    value: int = 20
    my_list: List[int] = field(default_factory=lambda: [1, 2, 3])

    def __hash__(self) -> int:
        return hash(str(vars(self)))



base_class = MyBaseClass()
sub_class = MySubclass()

print(base_class)
print(hash(base_class))

print(sub_class)
print(hash(sub_class))



# test_hashable: Dict["AbstractRif", None] = {}

# hashable_rif = HashableRif(subject="demo", body="Hello, Hope you like this over submission!", send_too=["me", "you"], namespace="rif.demo")
# hashable_rif_one = HashableRif(subject="demo", body="Hello, Hope you like this over submission!", send_too=["me", "you"], namespace="rif.demo")
# hashable_rif_two = HashableRif(subject="demo", body="Hello, Hope you like this over submission!", send_too=["me", "you"], namespace="rif.demo")


# hashable_rif()

# test_hashable[hashable_rif] = None
# test_hashable[hashable_rif_one] = None
# test_hashable[hashable_rif_two] = None

