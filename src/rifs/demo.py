from dataclasses import dataclass, field
from typing import Any

from rifs import transmit as _transmit
from rifs.core import AbstractRif


@dataclass
class DemoRif(AbstractRif):
    """The main duck class for testing positional arguments"""

    name: str = field(default="demo")
    subject: str = field(default="world")
    body: str = field(default="Hello, {subject}!")
    send_too: list = field(default_factory=list)
    lala: str = field(default="lala")

    def __post_init__(self):
        super().__post_init__()
        self.lala = self.name

    def __call__(self, *args, **kwargs) -> None:
        # Print subject
        self.pre_process()
        print(self.lala, "here")
        print(self.subject)
        print(self.body.format(subject=self.subject))

        print("Sending to:" + ", ".join(self.send_too))
        self.post_process()


# Build the rif object
if __name__ == "__main__":
    demo_rif_one = DemoRif(
        name="demo1",
        subject="demo",
        body="Hello, Hope you like this over submission!",
        send_too=["me", "you"],
        namespace="rifs.demo",
    )
    demo_rif_two = DemoRif(
        name="demo2",
        subject="demo",
        body="Hello, Hope you like this over submission!",
        send_too=["me", "you"],
        namespace="rifs.demo",
    )
    demo_rif_three = DemoRif(
        name="demo3",
        subject="demo",
        body="Hello, Hope you like this over submission!",
        send_too=["me", "you"],
        namespace="rifs.demo",
    )
    demo_rif_four = DemoRif(
        name="demo4",
        subject="demo",
        body="Hello, Hope you like this over submission!",
        send_too=["me", "you"],
        namespace="rifs.demo",
    )

    # Demo 5
    demo_rif_five = DemoRif(
        name="demo5",
        subject="demo",
        body="Hello, Hope you like this over submission!",
        send_too=["me", "you"],
        namespace="rifs.demo",
    )


#     # Dependency injection
    demo_rif_three.depend_on = [demo_rif_one, demo_rif_two]
    demo_rif_four.depend_on = [demo_rif_three, demo_rif_five]



    my_constructor = _transmit.Constructor(operations=[demo_rif_three, demo_rif_four, demo_rif_one, demo_rif_two, ])
    my_constructor.submit(ignore=True)
