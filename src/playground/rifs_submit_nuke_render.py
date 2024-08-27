from dataclasses import dataclass
import rifs


@dataclass
class SubmitRif(rifs.core.AbstractRif):
    # command_override = ["nuke", "-t"]

    def __call__(self):
        print("Submitting rif")
        pass


if __name__ == "__main__":

    submit_rif_instance = SubmitRif(namespace="playground.rifs_submit_nuke_render")
    print(submit_rif_instance)
    print(submit_rif_instance.command_override)
    rifs.only_one(submit_rif_instance)
